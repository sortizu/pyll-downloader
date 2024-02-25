from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from enum import Enum
import requests

class Status(Enum):
    NOT_STARTED = 0
    DOWNLOADING = 1
    PAUSED = 2
    COMPLETED = 3

class Download:
    def __init__(self, url, path, file_name):
        self.url = url
        self.path = path
        if file_name == "":
            self.file_name = url.split('/')[-1]
        self.status = Status.NOT_STARTED
        self.progress = 0
        self._total_size = 0
        self._thread_pool = ThreadPoolExecutor(max_workers=16)
        self._num_parts = 0
        self._data_downloaded = 0
        self._data_lock=Lock()
        request = requests.get(self.url, stream=True)
        self._total_size = int(request.headers.get('content-length', 0))

    def parallel_download(self,lo,hi,depth):
        if self._request is None:
            self.status = Status.DOWNLOADING
        if depth > 2:
            headers = {'Range': 'bytes=%d-%d' % (lo, hi)}
            response = requests.get(self.url, headers=headers, stream=True)
            full_path = self.path + 'part%d' % self._num_parts
            self._num_parts += 1
            with open(full_path, 'wb') as file:
                for data in response.iter_content(chunk_size=8192):
                    file.write(data)
                    self._data_lock.acquire()
                    self._data_downloaded += len(data)
                    self._data_lock.release()
        else:
            mid = (lo + hi) // 2
            left = self._thread_pool.submit(self.download, lo, mid, depth + 1)
            right = self._thread_pool.submit(self.download, mid, hi, depth + 1)
            if depth==0 and left.result() and right.result():
                file = open(self.path + self.file_name, 'wb')
                for i in range(self._num_parts):
                    with open('part%d' % i, 'rb') as part_file:
                        file.write(part_file.read())
                self.status = Status.COMPLETED

    def secuential_download(self):
        self.status = Status.DOWNLOADING
        response = requests.get(self.url, stream=True)
        full_path = self.path + self.file_name
        with open(full_path, 'wb') as file:
            for data in response.iter_content(chunk_size=8192):
                file.write(data)
                self._data_lock.acquire()
                self._data_downloaded += len(data)
                self._data_lock.release()
        self.status = Status.COMPLETED
    
    def get_progress(self):
        if self._total_size == 0:
            return 0
        return (self._data_downloaded / self._total_size) * 100
    
    def get_total_size(self):
        """
        Returns the total size of the file in bytes
        """
        return self._total_size
    def get_formatted_total_size(self):
        """
        Returns the total size of the file in a human-readable format
        """
        temp = self._total_size
        count = 0
        while temp > 1024:
            temp /= 1024
            count += 1
        size_units = ["B", "KB", "MB", "GB", "TB"]
        return f"{temp:.2f} {size_units[count]}"