import os
import logging


#Configure logging.
logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.INFO,
    force=True
)


#Number of spawned processes. Leaving 1 core for the main thread by default.
CPU_COUNT = os.cpu_count()
N_PROCS_DEFAULT = (CPU_COUNT - 1) if CPU_COUNT else 4
N_PROCS = int(os.getenv('N_PROCS', N_PROCS_DEFAULT))


#Maximum queue size after which the new tasks wont be accepted.
QUEUE_SIZE = int(os.getenv('QUEUE_SIZE', 1024))
