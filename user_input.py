import re, datetime, os, readline
import dateutil.tz

def formatDate(date):
    return date.astimezone(dateutil.tz.tzlocal()).strftime("%Y/%m/%d %H:%M")

class DateInputHandler:
    num12 = r"(\d{1,2})"
    hourPart = num12 + r":(\d{0,2})"
    t1 = re.compile(num12 + r" " + hourPart)
    t2 = re.compile(num12 + r"/" + num12 + r" " + hourPart)
    t3 = re.compile(r"(\d{4})" + r"/" + num12 + r"/" + num12 + r" " + hourPart)
    t4 = re.compile(r":" + num12)
    t5 = re.compile(hourPart)

    def __init__(self,
                 display,
                 default = None,
                 formatDateFunc = formatDate):
        self._display = display
        self._default = default if default != None else None
        self._formatDate = formatDateFunc

    def comp(self, text, state):
        # only provide one hint
        if state > 0:
            return None

        try:
            out = self.tryParse(text.strip(), self._default)
        except:
            return None
        return self._formatDate(out)
        
    def getInput(self):
        out = None
        if self._default == None:
            self._default = datetime.datetime.now(dateutil.tz.tzlocal())
        readline.clear_history()

        # put the default value into history
        readline.add_history(self._formatDate(self._default))

        # try to complete during typing.
        readline.set_completer_delims('\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.comp)

        # get user input until it's acceptable
        while out == None:
            inp = input(self._display + " [{}]: "
                        .format(self._formatDate(self._default)))
            if inp == "?":
                self.printSpec()
            else:
                try:
                    out = self.tryParse(inp.strip(), self._default)
                except Exception as e:
                    # although the value is not acceptable, give user
                    # a chance to modify it.
                    hist = inp.strip()
                    if len(hist) > 0:
                        readline.add_history(inp.strip())
                    self.printSpec()

        readline.clear_history()
        readline.set_completer()
        # print(">> {}: {}".format(self._display, out.strftime("%Y/%m/%d %H:%M")))
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
    def __init__(self,
                 display,
                 default = None,
                 allowEmpty = False):
        self._display = display
        self._allowEmpty = allowEmpty
        self._default = default

    def getInput(self):
        r = None
        readline.clear_history()
        if isinstance(self._default, str):
            readline.add_history(self._default)
        while r == None or \
              (not self._allowEmpty and len(r) == 0):
            r = input(self._display + "{}: ".format(
                "" if self._default == None else "[" + self._default + "]"
            )).strip()

            # use default if there's a default when user
            # just type enter.
            if len(r) == 0 and self._default != None:
                r = self._default
        readline.clear_history()
        return r

class HintedInputHandler(TextInputHandler):
    def __init__(self,
                 display,
                 hints,
                 default = None,
                 allowEmpty = False):
        super().__init__(display, default, allowEmpty)
        self._hints = hints

    def comp(self, txt, state):
        if state == 0:
            # build list
            self._comp_list = [s for s in self._hints if s[:len(txt)] == txt]
        return self._comp_list[state] if len(self._comp_list) > state else None

    def getInput(self):
        readline.set_completer_delims('\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.comp)
        r = super().getInput()
        readline.set_completer()
        readline.clear_history()
        return r

class TagsInputHandler:
    def __init__(self, display, hints, default = []):
        self._display = display
        self._hints = hints
        self._default = default

    def getInput(self):
        out = set(self._default)
        initHints = set(self._hints)
        while True:
            hints = initHints - out
            print("Current tag: [{}]".format(", ".join(out)))
            inp = HintedInputHandler(self._display + " [- to delete, empty to end]",
                                     hints,
                                     allowEmpty = True).getInput()
            if inp == "":
                break
            if inp[0] == '-':
                try: out.remove(inp[1:].strip())
                except: pass
            else:
                out.add(inp)
        return list(out)

class AmountInputHandler:
    def __init__(self, display, default = None):
        self._display = display
        self._default = default

    def getInput(self):
        out = None
        while out == None:
            inp = input(self._display + "{}: ".format(
                "" if self._default == None else "[{:.2f}]".format(self._default)
            )).strip()
            if len(inp) == 0 and self._default != None:
                out = self._default
            else:
                try: out = float(inp)
                except: pass
        return out

def getUserInput(csb,
                 originDate     = None,
                 originSummary  = None,
                 originType     = None,
                 originTags     = [],
                 originAmount   = None,
                 originCurrency = None,
                 originPayment  = None):
    out = {}
    if originDate != None:
        print("Date: " + formatDate(originDate))
    else:
        out["date"] = DateInputHandler("Date",
                                       originDate).getInput()

    out["summary"] = TextInputHandler("Summary",
                                      originSummary).getInput()
    out["type"] = HintedInputHandler("Type",
                                     csb.allType(),
                                     originType).getInput()
    out["tags"] = TagsInputHandler("Tags",
                                   csb.allTag(),
                                   originTags).getInput()
    out["amount"] = AmountInputHandler("Amount",
                                       originAmount).getInput()
    out["currency"] = "NTD"
    out["payment"] = HintedInputHandler("Payment method",
                                        csb.allPayment(),
                                        originPayment).getInput()
    return out
