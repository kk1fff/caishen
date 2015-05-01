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
        return cls.toBase36(int(date.timestamp()) * 100 + random.randint(0, 99))
        
    @classmethod
    def createFromDictionary(cls, dic, storage):
        out = cls(storage)
        out._date = dic["date"].astimezone(datetime.timezone.utc)
        out._summary = dic["summary"]
        out._type = dic["type"]
        out._tags = dic["tags"]
        out._amount = float(dic["amount"])
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

    # modification
    def store(self):
        self._storage.insert(self)

    def delete(self):
        self._deleted = True
        self.store()

    # immutable properties
    def date(self):
        return self._date

    def rId(self):
        return self._id

    def currency(self):
        return self._currency

    def deleted(self):
        return self._deleted

    # mutable properties
    def _assignIfSet(self, attr, exp_type, v):
        if isinstance(v, exp_type):
            setattr(self, attr, v)
        return getattr(self, attr)
    
    def amount(self, v = None):
        return self._assignIfSet("_amount", float, v)

    def summary(self, v = None):
        return self._assignIfSet("_summary", str, v)

    def typ(self, v = None):
        return self._assignIfSet("_type", str, v)

    def paymentMethod(self, v = None):
        return self._assignIfSet("_paymentMethod", str, v)

    def tags(self, v = None):
        return self._assignIfSet("_tags", list, v)

    def addTag(self, v):
        v = v.strip()
        if not v in self._tags:
            self._tags.append(v)

    def removeTag(self, v):
        try: self._tags.remove(v)
        except: pass

class RecordSet:
    def __init__(self):
        self._pool = dict() # id -> obj dictionary
        self._cache = dict()
        self._resetCache()

    def _resetCache(self):
        self._cache['types'] = None
        self._cache['tags'] = None
        self._cache['payments'] = None

    # helper function that get a value by iterating over pool and cache the
    # result. |cacheName| is the properties that store the data. |accessFunc|
    # defines a function, which takes a |record| and return a set that is
    # to be merged into our result.
    def _cachedPoolGetter(self, cacheName, accessFunc):
        if self._cache[cacheName] == None:
            out = set()
            for rec in self._pool.values():
                out = out | accessFunc(rec)
            self._cache[cacheName] = out
        return self._cache[cacheName]
        
    def insert(self, rec, replace):
        if (not replace) and (rec.rId() in self._pool):
            raise Exception("Given id is in the set already")
        self._resetCache()
        if rec.deleted() and rec.rId() in self._pool:
            del self._pool[rec.rId()]
        else:
            self._pool[rec.rId()] = rec

    def combine(self, other):
        self._resetCache()
        for i in other._pool.values():
            self.insert(i, False)

    def filterDate(self, start_date, end_date):
        self._resetCache()
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

    def unsorted(self):
        return self._pool.values()

    def types(self):
        return self._cachedPoolGetter('types',
                                      lambda r: { r.typ() })
    def tags(self):
        return self._cachedPoolGetter('tags',
                                      lambda r: set(r.tags()))
    def payments(self):
        return self._cachedPoolGetter('payments',
                                      lambda r: { r.paymentMethod() })

    def findById(self, recId):
        if recId in self._pool:
            return self._pool[recId]
        return None
