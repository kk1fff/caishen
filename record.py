import json, random, datetime
import dateutil.parser
random.seed()

class Record:
    @classmethod
    def toBase36(cls, num):
        ch = "0123456789abcdefghijklmnopqrstuvwxyz"
        out = ""
        while num > 0:
            out = out + ch[num % 36]
            num = int((num - (num % 36)) / 36)
        return out[::-1]

    @classmethod
    def createId(cls, date):
        return cls.toBase36(int(date.timestamp()) * 10000 + random.randint(0, 1000))
        
    @classmethod
    def createFromDictionary(cls, dic, storage):
        out = cls(storage)
        out._date = dic["date"].astimezone(datetime.timezone.utc)
        out._summary = dic["summary"]
        out._type = dic["type"]
        out._tags = dic["tags"]
        out._amount = dic["amount"]
        out._paymentMethod = dic["payment"]
        out._currency = dic["currency"]
        out._id = dic["id"] if "id" in dic else cls.createId(out._date)
        out._deleted = dic["deleted"] if "deleted" in dic else False
        return out

    @classmethod
    def createFromJson(cls, jsonStr, storage):
        d = json.loads(jsonStr)
        d["date"] = dateutil.parser.parse(d["date"])
        return cls.createFromDictionary(d, storage)
    
    def __init__(self, storage):
        self._storage = storage

        self._date = None
        self._summary = None
        self._type = None
        self._tags = None
        self._amount = None
        self._paymentMethod = None
        self._id = None
        self._currency = None
        self._deleted = None

    def toJson(self):
        return json.dumps({
            "date": self._date.isoformat(),
            "summary": self._summary,
            "type": self._type,
            "tags": self._tags,
            "amount": self._amount,
            "currency": self._currency,
            "payment": self._paymentMethod,
            "currency": self._currency,
            "id": self._id,
            "deleted": self._deleted
        })

    def date(self):
        return self._date

    def store(self):
        self._storage.insert(self)

    def rId(self):
        return self._id

class RecordSet:
    def __init__(self):
        self._pool = dict() # id -> obj dictionary

    def insert(self, rec, replace):
        if (not replace) and (rec.rId() in self._pool):
            raise Exception("Given id is in the set already")
        self._pool[rec.rId()] = rec

    def combine(self, other):
        for i in other._pool.values():
            self.insert(i, False)

    def filterDate(self, start_date, end_date):
        new_pool = dict()
        for k, v in self._pool.items():
            if v.date() < start_date:
                continue
            if v.date() > end_date:
                continue
            new_pool[k] = v
        self._pool = new_pool

    def dateSorted(self):
        return sorted(self._pool.values(),
                      key = lambda x: x.date())
