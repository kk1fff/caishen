
import re, datetime, calendar
import dateutil.tz

# get a new date object that is obtained by month + diff.
# this covers minus month and that case that the target month
# doesn't have that day.
def monthDiff(date, diff):
    m = (date.month - 1) + diff % 12 # using base 12 numbering system for calculating.
    y = date.year + diff // 12 + m // 12 # consider the carry of m.
    m = (m % 12) + 1 # transfer back to month system.
    d = min(date.day, calendar.monthrange(y, m)[1])
    return date.replace(y, m, d)

def yearDiff(date, diff):
    return date.replace(date.year + diff)

def dayDiff(date, diff):
    return date + datetime.timedelta(days = diff)
    
class RangeParser:
    monthMatcher = re.compile(r"(\d+)m$")
    yearMatcher = re.compile(r"(\d+)y$")
    dayMatcher = re.compile(r"(\d*)d{0,1}$")
    thisYearMatcher = re.compile(r"y$")
    thisMonthMatcher = re.compile(r"m$")
    def __init__(self, arg, now, arg2 = None):
        self._now = now
        self._start = None
        self._end = now
        self.parseSingle(arg)
    def parseSingle(self, arg):
        """Handle a single param to stand for a range"""
        number_filter = lambda s: 0 if len(s) == 0 else int(s)
        d1 = None
        matched = False

        m = self.dayMatcher.match(arg)
        if m != None:
            d1 = dayDiff(self._now, -number_filter(m.group(1)))
            matched = True

        m = self.thisYearMatcher.match(arg)
        if m != None and not matched:
            d1 = self._now.replace(month=1, day=1)
            matched = True

        m = self.thisMonthMatcher.match(arg)
        if m != None and not matched:
            d1 = self._now.replace(day=1)
            matched = True

        m = self.monthMatcher.match(arg)
        if m != None and not matched:
            d1 = monthDiff(self._now, -number_filter(m.group(1)))
            matched = True

        m = self.yearMatcher.match(arg)
        if m != None and not matched:
            d1 = yearDiff(self._now, -number_filter(m.group(1)))
            matched = True

        if not matched:
            raise Exception("Not match")

        self._start = d1.replace(hour=0, minute=0,
                                 second=0, microsecond=0)
    def start(self):
        return self._start
    def end(self):
        return self._end
        
class ViewCommand:
    def __init__(self, csb):
        self._csb = csb
    def run(self, argv):
        range_parser = None
        now = datetime.datetime.now(dateutil.tz.tzlocal())
        try:
            range_parser = RangeParser(argv[0] if len(argv) > 0 else "",
                                       now = now)
        except:
            print("Fail to parse argument")
            raise
        recs = self._csb.queryRange(range_parser.start(),
                                    range_parser.end())
        for rec in recs.dateSorted():
            print("{} {}".format(rec.date(), rec._amount))
