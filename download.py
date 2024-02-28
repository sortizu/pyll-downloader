from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
import os
from threading import Lock
from enum import Enum
import time
import requests

class Status(Enum):
    NOT_STARTED = 0
    DOWNLOADING = 1
    PAUSED = 2
    COMPLETED = 3

class DownloadType(Enum):
    SEQUENTIAL = 0
    PARALLEL = 1

class Download:
    def __init__(self, url, path, file_name, download_type=DownloadType.PARALLEL):
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
        self._request = requests.get(self.url, stream=True)
        self._total_size = int(self._request.headers.get('content-length', 0))
        self.start_time = 0
        self.download_time = 0
        self.download_type = download_type
        # Checks if the file already exists in the path, if it does, get the number of repeated files and add it to the file name
        count = 0
        normal_path = self.path + self.file_name
        if os.path.exists(normal_path):
            count += 1
        while os.path.exists(self.path + self.file_name.split('.')[-2] + f"_{count}.{self.file_name.split('.')[-1]}"):
            count += 1
        if count > 0:
            self.file_name = self.file_name.split('.')[-2] + f"_{count}." + self.file_name.split('.')[-1]


    def download(self):
        self.start_time = time.time()
        if self.download_type == DownloadType.PARALLEL:
            self.parallel_download(0, self._total_size, 0)
        else:
            self.secuential_download()

    def parallel_download(self,lo,hi,depth):
        self.status = Status.DOWNLOADING
        if depth > 1:
            headers = {'Range': 'bytes=%d-%d' % (lo, hi)}
            response = requests.get(self.url, headers=headers, stream=True)
            full_path = self.path + self.file_name.split('.')[-2] + '_part%d.' % self._num_parts
            self._num_parts += 1
            try:
                with open(full_path, 'wb') as file:
                    for data in response.iter_content(chunk_size=8192):
                        file.write(data)
                        self._data_lock.acquire()
                        self._data_downloaded += len(data)
                        self._data_lock.release()
                return True
            except Exception as e:
                print(e)
                return False
        else:
            mid = (lo + hi) // 2
            left = self._thread_pool.submit(self.parallel_download, lo, mid, depth + 1)
            right = self._thread_pool.submit(self.parallel_download, mid, hi, depth + 1)
            # Wait for the threads to finish
            left.result()
            right.result()
            if depth==0:
                # Merge the parts into a single file
                self.download_time = time.time() - self.start_time
                self.status = Status.COMPLETED
                file = open(self.path + self.file_name, 'wb')
                for i in range(self._num_parts):
                    new_path = self.path + self.file_name.split('.')[-2] + '_part%d.' % i
                    with open(new_path, 'rb') as part_file:
                        file.write(part_file.read())
                # Delete the parts
                for i in range(self._num_parts):
                    new_path = self.path + self.file_name.split('.')[-2] + '_part%d.' % i
                    os.remove(new_path)

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
        self.download_time = time.time() - self.start_time
    
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

    def pause(self):
        self.status = Status.PAUSED
    
    def stop(self):
        self._thread_pool.shutdown(wait=False)
        self.status = Status.NOT_STARTED
    
    def get_download_time(self):
        """
        Returns the time it took to download the file in seconds
        """
        new_time = 0
        if self.status == Status.NOT_STARTED:
            new_time = 0
        elif self.status == Status.DOWNLOADING:
            new_time = time.time() - self.start_time
        elif self.status == Status.COMPLETED:
            new_time = self.download_time
        return new_time
    def get_formatted_download_time(self):
        """
        Returns the time it took to download the file in a human-readable format
        """
        new_time = self.get_download_time()
        return time.strftime("%H:%M:%S", time.gmtime(new_time))