from jvorm import JsonMySQLBridge

bridge = JsonMySQLBridge(
    host="localhost",
    user="desfase",
    password="desfase",
    database="desfase",
    json_path_default="./clientes.json"  # JSON de entrada
)

bridge.load_from_json()  # usa ./datos.json por defecto

recovered = bridge.dump_to_json("./clientes_recuperado.json")

print("✅ Hecho. Resumen (primer nivel):")
for k, v in recovered.items():
    print(f"- {k}: {len(v)} elemento(s)")
