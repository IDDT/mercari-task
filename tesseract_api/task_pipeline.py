import os
import logging
import tempfile
from queue import Queue
from typing import Optional
from threading import Thread
from .adapters import ocr_image_file
from .config import N_PROCS, QUEUE_SIZE


class TaskPipeline:
    '''Class implementing asyncronous image OCR with multiple workers.
    Methods:
        append(img_bytes): Submit img_bytes for OCR and get a task_id.
        __contains__(task_id): Check if the task_id was created.
        __getitem__(task_id): Get the task result or None if not ready.
    '''
    def __init__(self):
        logging.info('Initializing task pipeline...')
        self.counter = 0
        self.temp_dir = tempfile.mkdtemp()
        self.task_queue = Queue(QUEUE_SIZE)
        self.results: dict[str, Optional[str]] = {}
        logging.info(f'Starting {N_PROCS} workers...')
        self.workers = []
        for _ in range(N_PROCS):
            self.workers.append(Thread(target=self._worker, daemon=True))
            self.workers[-1].start()
        logging.info('Initializing task pipeline complete.')

    def _worker(self):
        for task_id in iter(self.task_queue.get, None):
            filepath = os.path.join(self.temp_dir, task_id)
            self.results[task_id] = ocr_image_file(filepath)
            os.remove(filepath)
            self.task_queue.task_done()

    def append(self, img_bytes:bytes) -> str:
        #Gnerate task_id. Rotate to avoid unwieldy numbers.
        self.counter = self.counter + 1 if self.counter < 2**32 else 0
        task_id = hex(self.counter)[2:]
        #Write image to disk. This will avoid OOM crashes during peak loads.
        filepath = os.path.join(self.temp_dir, task_id)
        with open(filepath, 'wb') as f:
            f.write(img_bytes)
        #Create task_id result as not ready.
        self.results[task_id] = None
        #Put task to the queue.
        self.task_queue.put(task_id)
        return task_id

    def __contains__(self, task_id:str):
        return task_id in self.results

    def __getitem__(self, task_id:str) -> Optional[str]:
        if (result := self.results[task_id]) is not None:
            del self.results[task_id]
            return result
