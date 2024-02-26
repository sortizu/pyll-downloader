from concurrent.futures import ThreadPoolExecutor
from download import *
class DownloadManager:
    def __init__(self, max_concurrent_downloads: int):
        self.max_concurrent_downloads = max_concurrent_downloads
        self._running_downloads = set()
        self._download_list = []
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_downloads)
    
    def add_download(self, url: str, path: str, file_name: str):
        # Verify if the url is valid
        if not url.startswith("http"):
            return
        new_download = Download(url, path, file_name)
        self._download_list.append(new_download)
    
    def download_all(self):
        for dw in self._download_list:
            if dw.status == Status.NOT_STARTED:
                self.start_download(dw)

    def start_download(self, dw: Download):
        #self._running_downloads.add(dw)
        self.executor.submit(dw.secuential_download)

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