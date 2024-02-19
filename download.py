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
        self.file_name = file_name
        self.status = Status.NOT_STARTED
        self._progress = 0

    def download(self):
        self.status = Status.DOWNLOADING
        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(self.path + self.file_name, 'wb') as file:
            for data in response.iter_content(chunk_size=8192):
                file.write(data)
                self._progress += len(data)
                self._progress_percentage = self._progress / total_size * 100

        print(self.path + ' downloaded successfully')
        self.status = Status.COMPLETED

    def getProgress(self):
        return self._progress

    def pause(self):
        self.status = Status.PAUSED