import re, datetime, os, readline
import dateutil.tz

class DateInputHandler:
    num12 = r"(\d{1,2})"
    hourPart = num12 + r":(\d{0,2})"
    t1 = re.compile(num12 + r" " + hourPart)
    t2 = re.compile(num12 + r"/" + num12 + r" " + hourPart)
    t3 = re.compile(num12 + r"/" + num12 + r"/" + num12 + r" " + hourPart)
    t4 = re.compile(r":" + num12)
    t5 = re.compile(hourPart)

    def __init__(self, display):
        self._display = display

    def getInput(self):
        out = None
        now = datetime.datetime.now(dateutil.tz.tzlocal())
        while out == None:
            inp = input(self._display + " (ref: {}) [?]: "
                        .format(now.strftime("%Y/%m/%d %H:%M")))
            if inp == "?":
                self.printSpec()
            else:
                try:
                    out = self.tryParse(inp.strip(), now)
                except Exception as e:
                    self.printSpec()

        print(">> {}: {}".format(self._display, out.strftime("%Y/%m/%d %H:%M")))
        return out

    def tryParse(self, inp, now):
        if inp == "":
            return now
        yr = now.year
        mo = now.month
        da = now.day
        ho = now.hour
        mi = now.minute
        
        m = self.t1.match(inp)
        matched = False
        if m != None:
            da = int(m.group(1))
            ho = int(m.group(2))
            mi = int(m.group(3)) if m.group(3) != "" else 0
            matched = True

        m = self.t2.match(inp)
        if m != None and not matched:
            mo = int(m.group(1))
            da = int(m.group(2))
            ho = int(m.group(3))
            mi = int(m.group(4)) if m.group(4) != "" else 0
            matched = True

        m = self.t3.match(inp)
        if m != None and not matched:
            yr = int(m.group(1))
            mo = int(m.group(2))
            da = int(m.group(3))
            ho = int(m.group(4))
            mi = int(m.group(5)) if m.group(5) != "" else 0
            matched = True

        m = self.t4.match(inp)
        if m != None and not matched:
            mi = int(m.group(1))
            matched = True

        m = self.t5.match(inp)
        if m != None and not matched:
            ho = int(m.group(1))
            mi = int(m.group(2)) if m.group(2) != "" else 0
            matched = True

        if not matched:
            raise

        return datetime.datetime(yr, mo, da, ho, mi,
                                 tzinfo=dateutil.tz.tzlocal())

    def printSpec(self):
        print(" Date and time:")
        print("   <day> <hour>:[<minute>]")
        print("   <month>/<day> <hour>:[<minute>]")
        print("   <year>/<month>/<day> <hour>:[<minute>]")
        print(" Time:")
        print("   :<min>")
        print("   <hour>:[<min>]")
        print(" or just enter to accept reference")
        
class TextInputHandler:
    def __init__(self, display, allowEmpty = False):
        self._display = display
        self._allowEmpty = allowEmpty

    def getInput(self):
        r = None
        while r == None or \
              (not self._allowEmpty and len(r) == 0):
            r = input(self._display + ": ")
        return r

class HintedInputHandler:
    def __init__(self, display, hints, allowEmpty = False):
        self._display = display
        self._hints = hints
        self._allowEmpty = allowEmpty

    def comp(self, txt, state):
        if state == 0:
            # build list
            self._comp_list = [s for s in self._hints if s[:len(txt)] == txt]
        return self._comp_list[state] if len(self._comp_list) > state else None

    def getInput(self):
        readline.set_completer_delims('\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.comp)
        r = None
        while r == None or \
              (not self._allowEmpty and len(r) == 0):
            r = input(self._display + ": ")
        readline.set_completer()
        return r

class TagsInputHandler:
    def __init__(self, display, hints):
        self._display = display
        self._hints = hints
    def getInput(self):
        out = set()
        initHints = set(self._hints)
        while True:
            hints = initHints - out
            print("Current tag: [{}]".format(", ".join(out)))
            inp = HintedInputHandler(self._display + " [empty to end]",
                                     hints,
                                     allowEmpty = True).getInput()
            if inp == "":
                break
            out.add(inp)
        return list(out)

class AmountInputHandler:
    def __init__(self, display):
        self._display = display
    def getInput(self):
        out = None
        while out == None:
            try:
                out = int(input(self._display + ": ").strip())
            except:
                pass
        return out

class AddCommand:
    def __init__(self, csbook):
        self._csb = csbook

    def run(self, args):
        rec = self._csb.makeRecord(
            { "date":     DateInputHandler("Date").getInput(),
              "summary":  TextInputHandler("Summary").getInput(),
              "type":     HintedInputHandler("Type",
                                             self._csb.allType()).getInput(),
              "tags":     TagsInputHandler("Tags",
                                           self._csb.allTag()).getInput(),
              "amount":   AmountInputHandler("Amount").getInput(),
              "currency": "NTD",
              "payment":  HintedInputHandler("Payment method",
                                             self._csb.allPayment()).getInput() })
        rec.store()
