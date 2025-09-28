from datetime import datetime
import multiprocessing as mp

def trabajo(_):
    numero = 1.0000098
    print("empiezo")
    for i in range(0,10000000):
          numero *=1.00000000000654
    final = int(datetime.now().timestamp())
    return final #devolvemos cuándo terminó este proceso

if __name__ == "__main__":
    inicio = int(datetime.now().timestamp())

    with mp.Pool(processes=16) as pool:
        #ejecuta 16 veces el mismo bloque, en paralelo
        finales = pool.map(trabajo,range(0,16))

        #Usamos el último en terminar como referencia de 'final'
        final = max(finales)
        print("he tardado"+str(final-inicio)+" segundos")
