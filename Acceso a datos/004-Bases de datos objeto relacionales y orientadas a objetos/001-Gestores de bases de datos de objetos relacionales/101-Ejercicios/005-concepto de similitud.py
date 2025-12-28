frase = 'La vida es aquello que te ocurre mientras estás ocupado haciendo otros planes.'

# tokens
palabras = frase.lower().split(" ")
print(palabras) 

frase_alternativa_1 = "Aquello que te ocurre mientras haces otros planes, es la vida"
frase_alternativa_2 = "El éxito es la suma de pequeños esfuerzos repetidos día tras día."

# Voy a empezar con la frase 1
explotado2 = frase_alternativa_1.lower().split(" ")
contador = 0
for palabra in palabras:
  for palabra2 in explotado2:
    if palabra == palabra2:
      contador+= 1
print("Calificacion",contador)

# Voy a empezar con la frase 2
explotado2 = frase_alternativa_2.lower().split(" ")
contador = 0
for palabra in palabras:
  for palabra2 in explotado2:
    if palabra == palabra2:
      contador+= 1
print("Calificacion",contador)

