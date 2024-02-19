import urllib.request as request

# This method downloads the file from the given url and saves it to the given path
def download_file(url, path):
    response = request.urlopen(url)
    data = response.read()
    file = open(path, 'wb')
    file.write(data)
    file.close()
    print(path + ' downloaded successfully')

