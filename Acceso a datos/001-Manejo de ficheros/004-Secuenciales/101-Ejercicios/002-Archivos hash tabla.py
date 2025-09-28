import os
import hashlib
import json

try:
    os.mkdir("secuenciales")
    
except:
     pass

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


for persona in personas:
  cadena = persona['nombre']+persona['apellido']+str(persona['edad'])
  picadillo = hashlib.md5(cadena.encode()).hexdigest()
  print(picadillo)
  archivo = open ("hash/" +picadillo+ ".json",'w')
  json.dump(persona,archivo,indent=4)
  archivo.close()
  
# Ahora busco entre esos hashes

cadena = "Elena"+"Vargas Soto"+"34"
picadillo = hashlib.md5(cadena.encode()).hexdigest()
archivo = open("hash/"+picadillo+".json",'r')
contenido = json.loads(archivo)
print(contenido )
