import os
import requests
import threading
import urllib.request, urllib.error, urllib.parse
import time

# inisialisasi URL yang menuju kepada suatu gambar
url = "https://apod.nasa.gov/apod/image/1901/LOmbradellaTerraFinazzi.jpg"

# fungsi untuk membuat range byte untuk setiap thread
def buildRange(value, numsplits):
    lst = []
    for i in range(numsplits):
        if i == 0:
            lst.append('%s-%s' % (i, int(round(1 + i * value/(numsplits*1.0) + value/(numsplits*1.0)-1, 0))))
        else:
            lst.append('%s-%s' % (int(round(1 + i * value/(numsplits*1.0),0)), int(round(1 + i * value/(numsplits*1.0) + value/(numsplits*1.0)-1, 0))))
    return lst

# class untuk split byte yang haris di download sesuai dengan ukuran byte
class SplitBufferThreads(threading.Thread):
    """ Splits the buffer to ny number of threads
        thereby, concurrently downloading through
        ny number of threads.
    """

    # inisialisasi thread dengan url dan ukuran bytes
    def __init__(self, url, byteRange):
        super(SplitBufferThreads, self).__init__()
        self.__url = url
        self.__byteRange = byteRange
        self.req = None

    # request file sesuai dengan range byte
    # inisialisasi req class
    def run(self):
        self.req = urllib.request.Request(self.__url,  headers={'Range': 'bytes=%s' % self.__byteRange})

    # fungsi get byte yang sudah di download
    def getFileData(self):
        return urllib.request.urlopen(self.req).read()


def main(url=None, splitBy=3):
    # inisialisasi variable yang mengandung waktu fungsi main dijalankan
    start_time = time.time()

    # cek apakah variable url mengandung sebuah nilai selain None
    # jika url == None, keluar dari fungsi main
    # jika url != None, lanjutkan fungsi main
    if not url:
        print("Please Enter some url to begin download.")
        return

    # parsing isi url dengan '/' sebagai patokan split
    fileName = url.split('/')[-1]

    # request header dari url untuk mendapatkan ukuran file
    sizeInBytes = requests.head(url, headers={'Accept-Encoding': 'identity'}).headers.get('content-length', None)
    print("%s bytes to download." % sizeInBytes)

    # cek apakah variable sizeInBytes yang mengandung ukuran file mengandung sebuah nilai selain None
    # jika sizeInBytes == None, keluar dari fungsi main
    # jika sizeInBytes != None, lanjutkan fungsi main
    if not sizeInBytes:
        print("Size cannot be determined.")
        return

    # inisialisasi list kosong (buffer)
    dataLst = []

    # split proses download ke 3 thread (splitBy = 3)
    for idx in range(splitBy):
        # panggil fungsi buildRange
        # tentukan range byte yang harus di download oleh sebuah thread
        byteRange = buildRange(int(sizeInBytes), splitBy)[idx]

        # inisialisasi object SplitBufferThreads dengan url dan range byte yang harus di download
        bufTh = SplitBufferThreads(url, byteRange)

        # mulai thread
        bufTh.start()

        # tunggu hingga thread selesai
        bufTh.join()

        # append semua byte ke buffer (list)
        dataLst.append(bufTh.getFileData())

    # join bytes dalam buffer (list)
    content = b''.join(dataLst)
    if dataLst:

        # jika file sudah ada, hapus
        if os.path.exists(fileName):
            os.remove(fileName)

        # print jumlah waktu dari awal hingga akhir
        print("--- %s seconds ---" % str(time.time() - start_time))

        # write file
        with open(fileName, 'wb') as fh:
            fh.write(content)
        print("Finished Writing file %s" % fileName)

# run program
if __name__ == '__main__':

    # panggil fungsi main dengan url sebagai parameter
    main(url)