<?php
/**
 * templates/pedidos.php
 *
 * Formulario personalizado para INSERT/UPDATE en la tabla `pedidos`.
 *
 * Variables disponibles desde el microERP:
 * - $tabla
 * - $columnMeta
 * - $foreignKeys
 * - $primaryKey
 * - $conexion
 * - $template_mode  ('insert' | 'update')
 * - $fila_actual    (array en update, null en insert)
 * - $form_action    (URL para el <form action="...">)
 */

$is_update = isset($template_mode) && $template_mode === 'update';

// Valores para el formulario
if ($is_update) {
    $id_pedido             = $fila_actual['id_pedido']              ?? '';
    $id_cliente            = $fila_actual['id_cliente']             ?? '';
    $numero_pedido         = $fila_actual['numero_pedido']          ?? '';
    $fecha_pedido          = $fila_actual['fecha_pedido']           ?? '';
    $id_estado             = $fila_actual['id_estado']              ?? '';
    $id_estado_pago        = $fila_actual['id_estado_pago']         ?? '';
    $id_metodo_pago        = $fila_actual['id_metodo_pago']         ?? '';
    $id_metodo_envio       = $fila_actual['id_metodo_envio']        ?? '';
    $id_direccion_envio    = $fila_actual['id_direccion_envio']     ?? '';
    $id_direccion_facturacion = $fila_actual['id_direccion_facturacion'] ?? '';
    $subtotal              = $fila_actual['subtotal']               ?? '';
    $monto_impuestos       = $fila_actual['monto_impuestos']        ?? '';
    $coste_envio           = $fila_actual['coste_envio']            ?? '';
    $monto_descuento       = $fila_actual['monto_descuento']        ?? '';
    $monto_total           = $fila_actual['monto_total']            ?? '';
    $notas                 = $fila_actual['notas']                  ?? '';
} else {
    $id_pedido             = '';
    $id_cliente            = $_POST['id_cliente']             ?? '';
    $numero_pedido         = $_POST['numero_pedido']          ?? '';
    $fecha_pedido          = ''; // lo asigna la BD por defecto
    $id_estado             = $_POST['id_estado']              ?? '';
    $id_estado_pago        = $_POST['id_estado_pago']         ?? '';
    $id_metodo_pago        = $_POST['id_metodo_pago']         ?? '';
    $id_metodo_envio       = $_POST['id_metodo_envio']        ?? '';
    $id_direccion_envio    = $_POST['id_direccion_envio']     ?? '';
    $id_direccion_facturacion = $_POST['id_direccion_facturacion'] ?? '';
    $subtotal              = $_POST['subtotal']               ?? '';
    $monto_impuestos       = $_POST['monto_impuestos']        ?? '';
    $coste_envio           = $_POST['coste_envio']            ?? '';
    $monto_descuento       = $_POST['monto_descuento']        ?? '0.00';
    $monto_total           = $_POST['monto_total']            ?? '';
    $notas                 = $_POST['notas']                  ?? '';
}

/**
 * Helper: obtiene opciones para un campo FK como
 * [ ['value'=>..., 'label'=>...], ... ]
 */
$getOptionsForFk = function(string $fk_column) use ($foreignKeys, $conexion) {
    if (!isset($foreignKeys[$fk_column])) {
        return [];
    }
    $fk_info    = $foreignKeys[$fk_column];
    $tabla_fk   = $fk_info['tabla'];
    $columna_fk = $fk_info['columna'];

    $opts = [];
    $sql  = "SELECT * FROM ".$tabla_fk." ORDER BY ".$columna_fk." ASC";
    $res  = mysqli_query($conexion, $sql);
    if ($res) {
        while($row = mysqli_fetch_assoc($res)){
            $label_parts = [];
            foreach($row as $k=>$v){
                $label_parts[] = $v;
            }
            $opts[] = [
                'value' => $row[$columna_fk],
                'label' => implode(" | ", $label_parts)
            ];
        }
    }
    return $opts;
};

// Opciones para cada FK según el diccionario de claves foráneas
$options_clientes          = $getOptionsForFk('id_cliente');
$options_estados           = $getOptionsForFk('id_estado');
$options_estados_pago      = $getOptionsForFk('id_estado_pago');
$options_metodos_pago      = $getOptionsForFk('id_metodo_pago');
$options_metodos_envio     = $getOptionsForFk('id_metodo_envio');
$options_direcciones       = $getOptionsForFk('id_direccion_envio'); // mismo FK para envío y facturación
?>

<style>
/* Layout propio para este formulario de pedidos */
form.form-template-pedidos{
  columns:1 !important;
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:20px;
}

/* Bloques tipo tarjeta */
.form-template-pedidos .pedidos-block{
  background: radial-gradient(circle at 0 0, rgba(255,255,255,0.95), #f2f2ff);
  border-radius:var(--radio,10px);
  border:1px solid rgba(75,0,130,0.15);
  padding:18px 20px;
  box-shadow:0 8px 24px rgba(0,0,0,0.08);
  position:relative;
  overflow:hidden;
  break-inside:avoid;
}

/* Detalle decorativo */
.form-template-pedidos .pedidos-block::before{
  content:"";
  position:absolute;
  width:110px;
  height:110px;
  border-radius:50%;
  background:radial-gradient(circle, rgba(75,0,130,0.16), transparent 70%);
  top:-45px;
  right:-25px;
  opacity:0.9;
}

.form-template-pedidos .pedidos-block h3{
  margin-top:0;
  margin-bottom:6px;
  font-size:15px;
  color:var(--color_primario,indigo);
  position:relative;
  z-index:1;
}

.form-template-pedidos .pedidos-block small{
  display:block;
  font-size:11px;
  color:#777;
  margin-bottom:10px;
  position:relative;
  z-index:1;
}

/* Campos */
.form-template-pedidos label{
  display:block;
  font-weight:600;
  margin-bottom:4px;
  font-size:12px;
  color:#444;
  position:relative;
  z-index:1;
}

.form-template-pedidos input,
.form-template-pedidos select,
.form-template-pedidos textarea{
  width:100%;
  padding:9px 11px;
  margin-bottom:10px;
  border:1px solid rgba(75,0,130,0.28);
  border-radius:8px;
  font-size:13px;
  background-color:#ffffff;
  box-sizing:border-box;
  position:relative;
  z-index:1;
}

.form-template-pedidos textarea{
  min-height:80px;
  resize:vertical;
}

.form-template-pedidos input:focus,
.form-template-pedidos select:focus,
.form-template-pedidos textarea:focus{
  outline:none;
  border-color:var(--color_primario,indigo);
  box-shadow:0 0 0 2px rgba(75,0,130,0.18);
}

/* Footer botones */
.form-template-pedidos .pedidos-footer{
  display:flex;
  align-items:center;
  justify-content:flex-end;
  gap:12px;
  position:relative;
  z-index:1;
}

.form-template-pedidos .pedidos-footer input[type=submit]{
  background:linear-gradient(135deg, var(--color_primario,indigo), #9b59b6);
  color:white;
  cursor:pointer;
  border:none;
  font-weight:600;
  text-transform:uppercase;
  letter-spacing:0.8px;
  box-shadow:0 4px 12px rgba(75,0,130,0.5);
  padding:10px 20px;
  border-radius:999px;
}

.form-template-pedidos .pedidos-footer input[type=submit]:hover{
  box-shadow:0 6px 18px rgba(75,0,130,0.7);
  transform:translateY(-1px);
}
</style>

<form action="<?php echo htmlspecialchars($form_action, ENT_QUOTES); ?>" method="POST" class="form-template-pedidos">

  <!-- BLOQUE 1: Pedido & Cliente -->
  <div class="pedidos-block">
    <h3>Pedido &amp; cliente</h3>
    <small>Identificación del pedido y cliente asociado.</small>

    <?php if ($is_update && $id_pedido !== ''): ?>
      <label>ID pedido</label>
      <input type="text" value="<?php echo htmlspecialchars($id_pedido, ENT_QUOTES); ?>" disabled>
    <?php endif; ?>

    <label>Cliente</label>
    <select name="id_cliente" required>
      <option value="">— seleccionar cliente —</option>
      <?php foreach($options_clientes as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $id_cliente ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Número de pedido</label>
    <input
      type="text"
      name="numero_pedido"
      placeholder="Ej: PED-2025-0001"
      value="<?php echo htmlspecialchars($numero_pedido, ENT_QUOTES); ?>"
      required
    >

    <?php if ($is_update): ?>
      <label>Fecha de pedido</label>
      <input
        type="text"
        value="<?php echo $fecha_pedido ? htmlspecialchars($fecha_pedido, ENT_QUOTES) : '—'; ?>"
        disabled
      >
      <small>La fecha se establece automáticamente mediante <code>DEFAULT CURRENT_TIMESTAMP</code>.</small>
    <?php else: ?>
      <small>La fecha del pedido se establecerá automáticamente al crear el registro.</small>
    <?php endif; ?>
  </div>

  <!-- BLOQUE 2: Estado & pago -->
  <div class="pedidos-block">
    <h3>Estado &amp; pago</h3>
    <small>Control del estado del pedido y de su cobro.</small>

    <label>Estado del pedido</label>
    <select name="id_estado" required>
      <option value="">— seleccionar estado —</option>
      <?php foreach($options_estados as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $id_estado ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Estado del pago</label>
    <select name="id_estado_pago" required>
      <option value="">— seleccionar estado de pago —</option>
      <?php foreach($options_estados_pago as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $id_estado_pago ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Método de pago</label>
    <select name="id_metodo_pago" required>
      <option value="">— seleccionar método de pago —</option>
      <?php foreach($options_metodos_pago as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $id_metodo_pago ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>
  </div>

  <!-- BLOQUE 3: Envío & direcciones -->
  <div class="pedidos-block">
    <h3>Envío &amp; direcciones</h3>
    <small>Método de envío y direcciones vinculadas al pedido.</small>

    <label>Método de envío</label>
    <select name="id_metodo_envio" required>
      <option value="">— seleccionar método de envío —</option>
      <?php foreach($options_metodos_envio as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $id_metodo_envio ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Dirección de envío</label>
    <select name="id_direccion_envio" required>
      <option value="">— seleccionar dirección de envío —</option>
      <?php foreach($options_direcciones as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $id_direccion_envio ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Dirección de facturación</label>
    <select name="id_direccion_facturacion" required>
      <option value="">— seleccionar dirección de facturación —</option>
      <?php foreach($options_direcciones as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $id_direccion_facturacion ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>
  </div>

  <!-- BLOQUE 4: Totales -->
  <div class="pedidos-block">
    <h3>Totales</h3>
    <small>Importes económicos asociados al pedido.</small>

    <label>Subtotal</label>
    <input
      type="number"
      name="subtotal"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($subtotal, ENT_QUOTES); ?>"
      required
    >

    <label>Impuestos</label>
    <input
      type="number"
      name="monto_impuestos"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($monto_impuestos, ENT_QUOTES); ?>"
      required
    >

    <label>Coste de envío</label>
    <input
      type="number"
      name="coste_envio"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($coste_envio, ENT_QUOTES); ?>"
      required
    >

    <label>Descuento</label>
    <input
      type="number"
      name="monto_descuento"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($monto_descuento, ENT_QUOTES); ?>"
    >

    <label>Total</label>
    <input
      type="number"
      name="monto_total"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($monto_total, ENT_QUOTES); ?>"
      required
    >
    <small>
      Puedes calcular el total en tu lógica de negocio
      (por ejemplo, subtotal + impuestos + envío − descuento)
      y sólo mostrarlo aquí, o permitir edición manual.
    </small>
  </div>

  <!-- BLOQUE 5: Notas -->
  <div class="pedidos-block">
    <h3>Notas</h3>
    <small>Información adicional relevante para el pedido.</small>

    <label>Notas</label>
    <textarea
      name="notas"
      placeholder="Observaciones del cliente, instrucciones especiales, notas internas..."
    ><?php echo htmlspecialchars($notas, ENT_QUOTES); ?></textarea>
  </div>

  <!-- BLOQUE 6: Botón -->
  <div class="pedidos-block pedidos-footer">
    <input
      type="submit"
      value="<?php echo $is_update ? 'Guardar cambios' : 'Crear pedido'; ?>"
    >
  </div>

</form>

