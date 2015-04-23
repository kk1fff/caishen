from record import Record
from storage import Storage

class CSBook:
    def __init__(self, storage):
        self._storage = storage

    def makeRecord(self, dic):
        return Record.createFromDictionary(dic, self._storage)

    def queryRange(self, start_date, end_date):
        return self._storage.list(start_date, end_date)

def CSBookBuilder(config):
    return CSBook(Storage(config.storagePath()))
