from record import Record, RecordSet
import os, datetime

## A file contains 10 days of data.
BASEDATE = datetime.datetime(1984, 12, 21, tzinfo=datetime.timezone.utc)

def blockNumber(date):
    return (date - BASEDATE).days//10
    
def fileNameByBlock(block_number):
    return "financial_{:08}.jsonl".format(block_number)

def fileNameGenerator(start_date, end_date):
    first_block = blockNumber(start_date)
    last_block = blockNumber(end_date)
    while first_block <= last_block:
        yield fileNameByBlock(first_block)
        first_block = first_block + 1

class Storage:
    @classmethod
    def ensurePath(cls, path):
        if os.path.isdir(path):
            return
        if os.path.isfile(path):
            # cannot be a file
            raise Exception("{} is a file".format(path))
        os.makedirs(path)

    def __init__(self, path):
        self.ensurePath(path)
        self._path = path

    def pathnameByBlock(self, block_number):
        return os.path.join(self._path, fileNameByBlock(block_number))

    def pathnameByDate(self, date):
        return self.pathnameByBlock(blockNumber(date))

    def pathname(self, fn):
        return os.path.join(self._path, fn)
    
    def loadRecordsFromFile(self, fn):
        out = RecordSet()
        try:
            with open(fn, "r") as f:
                while True:
                    line = f.readline()
                    if line == "":
                        break
                    out.insert(Record.createFromJson(line.strip(), self),
                               replace = True)
        except FileNotFoundError: pass
        return out

    def insert(self, rec):
        # find file, append.
        with open(self.pathnameByDate(rec.date()), "a") as f:
            f.write(rec.toJson() + "\n")
            f.close()

    def list(self, start_date, end_date):
        out = RecordSet()
        for fn in fileNameGenerator(start_date, end_date):
            out.combine(self.loadRecordsFromFile(self.pathname(fn)))
        out.filterDate(start_date, end_date)
        return out

