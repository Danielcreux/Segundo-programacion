import json 

agenda =[
    {
        "nombre":"Joshue Daniel",
        "telefono":["8989789","8989789","8989789"],
        "email":"info@joshue.com",
    },
     {
        "nombre":"Juan Luis",
        "telefono":["99000","90000","990090"],
        "email":"info@Luis.com",
    },
    
]

archivo = open("agenda.json",'w')
json.dump("agenda",archivo,indent=4)
