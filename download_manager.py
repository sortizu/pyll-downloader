from concurrent.futures import ThreadPoolExecutor
from download import *
class DownloadManager:
    def __init__(self, max_concurrent_downloads: int):
        self.max_concurrent_downloads = max_concurrent_downloads
        self._running_downloads = set()
        self._download_list = []
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_downloads)
    
    def add_download(self, url: str, path: str, file_name: str, download_type: DownloadType = DownloadType.SEQUENTIAL):
        new_download = Download(url, path, file_name, download_type)
        self._download_list.append(new_download)
    
    def download_all(self):
        for dw in self._download_list:
            if dw.status == Status.NOT_STARTED:
                self.start_download(dw)

    def start_download(self, dw: Download):
        #self._running_downloads.add(dw)
        self.executor.submit(dw.download)

    def pause_all(self):
        for download in self._download_list:
            download.pause()
    
    def get_download_list(self):
        return self._download_list

    def is_valid_url(self, url: str):
        return url.startswith("http")
    
    def is_url_repeated(self, url: str):
        for dw in self._download_list:
            if dw.url == url:
                return True
        return False

    def get_metrics(self):
        sequential_time = 0
        parallel_time = 0
        for dw in self._download_list:
            if dw.download_type == DownloadType.SEQUENTIAL:
                sequential_time += dw.get_download_time()
            else:
                parallel_time += dw.get_download_time()
        average_sequential_time = sequential_time / (len(self._download_list)/2)
        average_parallel_time = parallel_time / (len(self._download_list)/2)
        speedup = average_sequential_time/average_parallel_time 
        efficiency = speedup / 6
        print(f"Average sequential time: {average_sequential_time}")
        print(f"Average parallel time: {average_parallel_time}")
        print(f"Speedup: {speedup}")
        print(f"Efficiency: {efficiency}")
        return [average_sequential_time, average_parallel_time, speedup, efficiency]

    def terminate(self):
        for dw in self._download_list:
            dw.stop()
        self.executor.shutdown(wait=False)
        print("Download manager closed")