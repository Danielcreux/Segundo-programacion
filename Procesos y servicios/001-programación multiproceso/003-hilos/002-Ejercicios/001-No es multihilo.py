from datetime import datetime

inicio= int(datetime.now().timestamp())

numero= 1.000000098
print("empiezo")
for i in range (0,10000000):
    numero *=1.000000000654
final = int(datetime.now().timestamp())
print("he tardado"+str(final-inicio)+"segundos")
