from mpi4py import MPI
import socket
import platform

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
host = socket.gethostname()
os_info = platform.system()

print(f"Hello from rank {rank}/{size} on host {host} ({os_info})")