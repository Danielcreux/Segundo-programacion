clientes =[{
    "nombre":"Joshue Daniel",
    "apellidos":"Freire Sanchez",
    "emails":[
        {
            "tipo":"personal",
            "direcciones":[
                "info@joshue.com",
                "joshue@gmail.com"
            ]
        },
        {
             "tipo":"empresa",
            "direcciones":[
                "info@danielcreux.com"
            ]
        }
    ]
},{
    "nombre":"Joshue Daniel",
    "apellidos":"Freire Sanchez",
    "emails":[
        {
            "tipo":"personal",
            "direcciones":[
                "info@joshue.com",
                "joshue@gmail.com"
            ]
        },
        {
             "tipo":"empresa",
            "direcciones":[
                "info@danielcreux.com"
            ]
        }
    ]
}
]

muestra = clientes[0]
print(muestra)

for clave in muestra.keys():
    print(clave)
    print(type(muestra[clave]))
    if type(muestra[clave]) == str:
        print("Lo voy a convertir en una columna de SQL que será de tipo varchar")
    elif type(muestra[clave]) == list:
        print("Lo voy a convertir en una externa de SQL")
    elif type(muestra[clave]) == int:
        print("Lo voy a convertir en una columna de SQL que será de tipo int")
    elif:
        print("No hay ninguna conversión por realizar")
        
    
    