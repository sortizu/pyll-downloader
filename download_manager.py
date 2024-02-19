from concurrent.futures import ThreadPoolExecutor
import download
class DownloadManager:
    def __init__(self, max_concurrent_downloads: int):
        self.max_concurrent_downloads = max_concurrent_downloads
        self._running_downloads = set()
        self._download_list = []
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_downloads)
    
    def add_download(self, url: str, path: str, file_name: str):
        download = download.Download(url, path, file_name)
        self._download_list.append(download)
    
    def download_all(self):
        with self.executor:
            for download in self._download_list:
                self.executor.submit(download.download)

    def start_download(self, download: download.Download):
        #self._running_downloads.add(download)
        self.executor.submit(download.download)

    def pause_all(self):
        for download in self._download_list:
            download.pause()
    
    def get_download_list(self):
        return self._download_list