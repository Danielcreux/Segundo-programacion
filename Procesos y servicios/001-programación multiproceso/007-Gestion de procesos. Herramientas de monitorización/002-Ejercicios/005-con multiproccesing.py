import multiprocessing

num_cores = multiprocessing.cpu_count()
print(f"You have {num_cores} CPU cores.")
