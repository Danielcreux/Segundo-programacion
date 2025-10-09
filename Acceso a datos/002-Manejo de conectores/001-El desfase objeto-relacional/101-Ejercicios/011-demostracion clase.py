#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import hashlib
import mysql.connector
from collections import defaultdict, deque

class JsonMySQLBridge:
    """
    Convierte JSON<->MySQL de forma recursiva.
    Regla base: cada CLAVE del objeto raíz del JSON es una TABLA TOP-LEVEL.
    Las subestructuras (dict/list) se materializan como tablas hijas con FK al padre.
    Las listas de escalares se almacenan como (parent_id, idx, valor).
    """

    # ===================== CONSTRUCCIÓN =====================
    def __init__(self, host, user, password, database, json_path_default="./datos.json"):
        self.DB = dict(host=host, user=user, password=password, database=database)
        self.JSON_PATH = json_path_default

        # estado temporal para el ciclo "escritura" (json->mysql)
        self.tables = {}      # name -> TableDef
        self.edges = set()    # (parent, child)
        self._conn = None
        self._cur = None

    # ===================== IDENT & TYPES =====================
    @staticmethod
    def _ident(name: str) -> str:
        """Sanitiza identificadores MySQL (tabla/col)."""
        name = (name or "").strip().lower()
        name = re.sub(r'[^a-z0-9_]+', '_', name)
        name = re.sub(r'_+', '_', name).strip('_')
        if not name:
            name = "col"
        if name[0].isdigit():
            name = "n_" + name
        if name in {"index", "key", "primary", "value"}:
            name = "_" + name
        return name

    @staticmethod
    def _cap_name(name: str, maxlen: int = 64) -> str:
        """Corta y añade hash si excede maxlen (para constraints/índices)."""
        if len(name) <= maxlen:
            return name
        h = hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]
        keep = maxlen - 1 - len(h)
        if keep < 1:
            keep = maxlen - len(h)
        return f"{name[:keep]}_{h}"

    def _fk_name(self, child: str, parent: str) -> str:
        return self._cap_name(f"fk_{child}_{parent}", 64)

    def _idx_name(self, child: str, parent: str) -> str:
        return self._cap_name(f"fk_{child}_{parent}", 64)

    @staticmethod
    def _sql_scalar_type(v):
        if isinstance(v, bool):  return "TINYINT(1)"
        if isinstance(v, int):   return "INT"
        if isinstance(v, float): return "DOUBLE"
        return "TEXT"

    @staticmethod
    def _merge_type(a, b):
        if a == b: return a
        pair = {a, b}
        if "TEXT" in pair: return "TEXT"
        if pair == {"INT","DOUBLE"}: return "DOUBLE"
        if pair == {"TINYINT(1)","INT"}: return "INT"
        return "TEXT"

    def _join_path(self, *parts) -> str:
        return self._ident("_".join([self._ident(p) for p in parts if p]))

    # ===================== MODELO DE TABLA =====================
    class TableDef:
        """kind: 'dict' | 'list_scalar'"""
        def __init__(self, name, parent=None, relname=None, kind='dict', ident_fn=None):
            self.name = ident_fn(name) if ident_fn else name
            self.parent = parent       # nombre tabla padre o None
            self.relname = relname     # nombre del campo en el padre
            self.kind = kind
            self.columns = {}          # solo para dict: col -> tipo SQL
            self.children = set()      # nombres de tablas hijas

    def _ensure_table(self, name, parent=None, relname=None, kind='dict'):
        tname = self._ident(name)
        if tname not in self.tables:
            self.tables[tname] = self.TableDef(tname, parent, relname, kind, self._ident)
        else:
            # subir de list_scalar a dict si hace falta
            if self.tables[tname].kind == 'list_scalar' and kind == 'dict':
                self.tables[tname].kind = 'dict'
        if parent:
            p = self._ident(parent)
            self.edges.add((p, tname))
            self.tables[p].children.add(tname)
        return self.tables[tname]

    # ===================== INFERENCIA (RECURSIVA) =====================
    def _infer_value(self, path_table: str, value, parent_table: str | None, relname: str | None):
        if isinstance(value, dict):
            t = self._ensure_table(path_table, parent_table, relname, kind='dict')
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    self._infer_value(self._join_path(path_table, k), v, t.name, k)
                else:
                    col = self._ident(k)
                    ttype = self._sql_scalar_type(v)
                    t.columns[col] = self._merge_type(t.columns.get(col, ttype), ttype)

        elif isinstance(value, list):
            elem_kind = "scalar"
            for el in value:
                elem_kind = "dict" if isinstance(el, dict) else "scalar"
                break
            if elem_kind == "dict":
                t = self._ensure_table(path_table, parent_table, relname, kind='dict')
                for el in value:
                    if not isinstance(el, dict):
                        continue
                    for k, v in el.items():
                        if isinstance(v, (dict, list)):
                            self._infer_value(self._join_path(path_table, k), v, t.name, k)
                        else:
                            col = self._ident(k)
                            ttype = self._sql_scalar_type(v)
                            t.columns[col] = self._merge_type(t.columns.get(col, ttype), ttype)
            else:
                self._ensure_table(path_table, parent_table, relname, kind='list_scalar')

        else:
            if parent_table is None:
                t = self._ensure_table(path_table, None, relname, kind='dict')
                t.columns['valor'] = self._merge_type(t.columns.get('valor', self._sql_scalar_type(value)),
                                                      self._sql_scalar_type(value))

    # ===================== TOPOLOGÍA & DDL =====================
    def _topo_tables(self):
        indeg = defaultdict(int)
        graph = defaultdict(list)
        for p, c in self.edges:
            graph[p].append(c)
            indeg[c] += 1
            if p not in indeg:
                indeg[p] = indeg[p]
        roots = [t for t in self.tables if indeg[t] == 0]
        q = deque(roots); out = []; seen = set()
        while q:
            u = q.popleft()
            if u in seen: continue
            seen.add(u); out.append(u)
            for v in graph[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        for t in self.tables:
            if t not in seen: out.append(t)
        return out

    def _drop_entire_schema(self, cursor, dbname: str):
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        try:
            cursor.execute("""
                SELECT TABLE_NAME FROM information_schema.tables
                WHERE table_schema = %s
            """, (dbname,))
            for (tname,) in cursor.fetchall():
                cursor.execute(f"DROP TABLE IF EXISTS `{tname}`;")
        finally:
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

    def _create_all(self, cursor):
        order = self._topo_tables()
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
        try:
            for t in reversed(order):
                cursor.execute(f"DROP TABLE IF EXISTS `{t}`;")

            for tname in order:
                t = self.tables[tname]
                cols = ["`Identificador` INT NOT NULL AUTO_INCREMENT"]
                if t.parent:
                    cols.append(f"`{t.parent}_id` INT NOT NULL")
                if t.kind == 'dict':
                    for c, typ in t.columns.items():
                        cols.append(f"`{self._ident(c)}` {typ} DEFAULT NULL")
                else:
                    cols += ["`idx` INT NOT NULL", "`valor` TEXT DEFAULT NULL"]
                cols.append("PRIMARY KEY (`Identificador`)")

                fk_idx_sql = ""
                fk_sql = ""
                if t.parent:
                    keyn = self._idx_name(t.name, t.parent)
                    fkn = self._fk_name(t.name, t.parent)
                    fk_idx_sql = f", KEY `{keyn}` (`{t.parent}_id`)"
                    fk_sql = (f", CONSTRAINT `{fkn}` FOREIGN KEY (`{t.parent}_id`)"
                              f" REFERENCES `{t.parent}` (`Identificador`)"
                              f" ON DELETE CASCADE ON UPDATE CASCADE")

                ddl = f"""CREATE TABLE `{t.name}` (
                  {", ".join(cols)}
                  {fk_idx_sql}
                  {fk_sql}
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
                cursor.execute(ddl)
        finally:
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

    # ===================== INSERT (RECURSIVA) =====================
    def _insert_list_scalar(self, cursor, tdef, value, parent_id: int | None):
        if not isinstance(value, list): value = [value]
        sql = f"INSERT INTO `{tdef.name}` (`{tdef.parent}_id`, `idx`, `valor`) VALUES (%s, %s, %s)"
        for i, el in enumerate(value):
            if isinstance(el, (dict, list)):
                try:
                    val = json.dumps(el, ensure_ascii=False)
                except Exception:
                    val = None
            else:
                val = el
            cursor.execute(sql, (parent_id, i, val))

    def _insert_dict_row(self, cursor, tdef, data: dict, parent_id: int | None):
        cols = []
        vals = []
        for c in tdef.columns:
            cols.append(f"`{self._ident(c)}`")
            v = data.get(c, None)
            if isinstance(v, (dict, list)): v = None
            vals.append(v)
        if tdef.parent:
            cols.insert(0, f"`{tdef.parent}_id`")
            vals.insert(0, parent_id)

        if cols:
            sql = f"INSERT INTO `{tdef.name}` ({', '.join(cols)}) VALUES ({', '.join(['%s']*len(cols))})"
            cursor.execute(sql, vals)
        else:
            if tdef.parent:
                cursor.execute(f"INSERT INTO `{tdef.name}` (`{tdef.parent}_id`) VALUES (%s)", (parent_id,))
            else:
                cursor.execute(f"INSERT INTO `{tdef.name}` () VALUES ()")

        new_id = cursor.lastrowid

        # hijos
        for k, v in data.items():
            if not isinstance(v, (dict, list)):
                continue
            child_name = self._join_path(tdef.name, k)
            child = self.tables.get(child_name)
            if child is None:
                if isinstance(v, dict):
                    child = self._ensure_table(child_name, tdef.name, k, kind='dict')
                    self._insert_dict_row(cursor, child, {}, new_id)
                continue
            if child.kind == 'dict':
                if isinstance(v, dict):
                    self._insert_dict_row(cursor, child, v, new_id)
                else:
                    for el in v:
                        if isinstance(el, dict):
                            self._insert_dict_row(cursor, child, el, new_id)
            else:
                self._insert_list_scalar(cursor, child, v, new_id)
        return new_id

    # ===================== API (WRITE) =====================
    def load_from_json(self, json_path: str | None = None):
        """Borra todas las tablas y carga el JSON a MySQL."""
        jp = json_path or self.JSON_PATH
        with open(jp, "r", encoding="utf-8") as f:
            root = json.load(f)
        return self.load_from_dict(root)

    def load_from_dict(self, root: dict):
        if not isinstance(root, dict):
            raise ValueError("El JSON raíz debe ser un objeto: cada clave es una tabla padre top-level.")

        # Inferencia de esquema
        self.tables.clear(); self.edges.clear()
        for top_key, top_val in root.items():
            top_table = self._ident(top_key)
            if isinstance(top_val, list):
                for el in top_val:
                    self._infer_value(top_table, el, parent_table=None, relname=None)
            else:
                self._infer_value(top_table, top_val, parent_table=None, relname=None)

        # Conectar, reset y crear
        self._conn = mysql.connector.connect(**self.DB)
        self._cur = self._conn.cursor()
        self._drop_entire_schema(self._cur, self.DB["database"])
        self._conn.commit()
        self._create_all(self._cur)
        self._conn.commit()

        # Insertar datos
        for top_key, top_val in root.items():
            top_table = self.tables[self._ident(top_key)]
            if isinstance(top_val, list):
                for el in top_val:
                    row = el if isinstance(el, dict) else {"valor": el}
                    self._insert_dict_row(self._cur, top_table, row, parent_id=None)
            elif isinstance(top_val, dict):
                self._insert_dict_row(self._cur, top_table, top_val, parent_id=None)
            else:
                self._insert_dict_row(self._cur, top_table, {"valor": top_val}, parent_id=None)

        self._conn.commit()
        self._cur.close()
        self._conn.close()
        self._cur = None; self._conn = None
        return True

    # ===================== API (READ) =====================
    @staticmethod
    def _fetchall_dict(cur, sql, params=None):
        cur.execute(sql, params or ())
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

    @staticmethod
    def _is_list_scalar_table(columns: set[str]) -> bool:
        return "idx" in columns and "valor" in columns

    def _child_field_name(self, parent: str, child: str) -> str:
        prefix = parent + "_"
        if child.startswith(prefix):
            return child[len(prefix):]
        return child

    def dump_to_json(self, output_path: str = "./dump_recuperado.json") -> dict:
        """Lee toda la BD y reconstruye el dict raíz; además, guarda el JSON."""
        conn = mysql.connector.connect(**self.DB)
        cur = conn.cursor()
        db = self.DB["database"]

        # Tablas
        tables = [r["TABLE_NAME"] for r in self._fetchall_dict(
            cur,
            "SELECT TABLE_NAME FROM information_schema.tables WHERE table_schema=%s AND TABLE_TYPE='BASE TABLE'",
            (db,)
        )]
        if not tables:
            raise RuntimeError("No hay tablas en la base de datos.")

        # Columnas
        table_columns = {}
        for t in tables:
            rows = self._fetchall_dict(cur, """
                SELECT COLUMN_NAME
                FROM information_schema.columns
                WHERE table_schema=%s AND table_name=%s
                ORDER BY ORDINAL_POSITION
            """, (db, t))
            table_columns[t] = [r["COLUMN_NAME"] for r in rows]

        # FKs
        rels = self._fetchall_dict(cur, """
            SELECT
              kcu.TABLE_NAME AS child_table,
              kcu.COLUMN_NAME AS child_column,
              kcu.REFERENCED_TABLE_NAME AS parent_table,
              kcu.REFERENCED_COLUMN_NAME AS parent_column
            FROM information_schema.KEY_COLUMN_USAGE kcu
            WHERE kcu.TABLE_SCHEMA=%s
              AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
        """, (db,))

        parent_of = {}
        fk_col_of_child = {}
        children_of = defaultdict(list)
        for r in rels:
            child = r["child_table"]
            parent = r["parent_table"]
            parent_of[child] = parent
            fk_col_of_child[child] = r["child_column"]
            children_of[parent].append(child)

        root_tables = [t for t in tables if t not in parent_of]

        # Cache de filas
        all_rows = {}
        for t in tables:
            all_rows[t] = self._fetchall_dict(cur, f"SELECT * FROM `{t}`")

        # Indexados por padre
        child_rows_by_parent = defaultdict(list)
        for child in parent_of:
            fk = fk_col_of_child[child]
            for row in all_rows[child]:
                pid = row.get(fk)
                if pid is not None:
                    child_rows_by_parent[(child, pid)].append(row)

        def build_node(table: str, row: dict) -> dict:
            cols = table_columns[table]
            fk_col = fk_col_of_child.get(table)
            scalar_cols = [c for c in cols if c not in {"Identificador", "idx", "valor"} and c != fk_col]

            node = {}
            for c in scalar_cols:
                node[c] = row.get(c)

            for child in children_of.get(table, []):
                rel_field = self._child_field_name(table, child)
                child_cols = set(table_columns[child])
                rows_child = child_rows_by_parent.get((child, row["Identificador"]), [])
                if not rows_child:
                    continue

                if self._is_list_scalar_table(child_cols):
                    seq = sorted(
                        [(rc.get("idx"), rc.get("valor")) for rc in rows_child],
                        key=lambda x: (x[0] if x[0] is not None else 0)
                    )
                    node[rel_field] = [val for _, val in seq]
                else:
                    if len(rows_child) == 1:
                        node[rel_field] = build_node(child, rows_child[0])
                    else:
                        node[rel_field] = [build_node(child, r) for r in rows_child]
            return node

        result = {}
        for rt in root_tables:
            rows = sorted(all_rows[rt], key=lambda r: r["Identificador"])
            result[rt] = [build_node(rt, r) for r in rows]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        cur.close(); conn.close()
        return result


# ===================== DEMO =====================
if __name__ == "__main__":
    # Configura tus credenciales y el path del JSON
    bridge = JsonMySQLBridge(
        host="localhost",
        user="desfase",
        password="desfase",
        database="desfase",
        json_path_default="./clientes.json"  # JSON de entrada
    )

    # ---- 1) ESCRIBIR: JSON -> MySQL ----
    # Carga el JSON y crea toda la estructura + inserta datos
    bridge.load_from_json()  # usa ./datos.json por defecto

    # ---- 2) LEER: MySQL -> JSON ----
    recovered = bridge.dump_to_json("./clientes_reconstruidos.json")

    print("✅ Hecho. Resumen (primer nivel):")
    for k, v in recovered.items():
        print(f"- {k}: {len(v)} elemento(s)")
