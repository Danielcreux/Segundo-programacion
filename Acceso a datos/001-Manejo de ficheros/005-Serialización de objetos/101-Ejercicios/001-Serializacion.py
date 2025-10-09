import json 

personas = [
  {
    "nombre": "Elena",
    "apellido": "Vargas Soto",
    "edad": 34,
    "ciudad": "Madrid",
    "profesion": "Ingeniera de Software"
  },
  {
    "nombre": "Kenji",
    "apellido": "Tanaka",
    "edad": 28,
    "ciudad": "Kioto",
    "profesion": "Diseñador Gráfico"
  },
  {
    "nombre": "Marcus",
    "apellido": "Johnson",
    "edad": 42,
    "ciudad": "Chicago",
    "profesion": "Periodista Deportivo"
  },
  {
    "nombre": "Aisha",
    "apellido": "Al-Jamil",
    "edad": 25,
    "ciudad": "Dubái",
    "profesion": "Arquitecta"
  },
  {
    "nombre": "Giovanni",
    "apellido": "Rossi",
    "edad": 67,
    "ciudad": "Nápoles",
    "profesion": "Jubilado"
  }
]

print (personas)
type(personas)
cadena = json.dumps(personas)
print(cadena)
print(type(cadena))

archivo = open("basededatos.dat",'w')
archivo.write(cadena)
archivo.close()
print(cadena)

