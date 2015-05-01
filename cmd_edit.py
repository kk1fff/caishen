from user_input import getUserInput

class EditCommand:
    def __init__(self, csb):
        self._csb = csb
    def run(self, argv):
        if len(argv) < 1:
            raise Exception("ID isn't specified")

        recId = argv[0]
        rec = self._csb.findById(recId)
        if rec == None:
            raise Exception("ID {} is not found.".format(recId))

        user_inp = getUserInput(self._csb,
                                originDate = rec.date(),
                                originSummary = rec.summary(),
                                originType = rec.typ(),
                                originTags = rec.tags(),
                                originAmount = rec.amount(),
                                originCurrency = rec.currency(),
                                originPayment = rec.paymentMethod())

        rec.amount(user_inp["amount"])
        rec.summary(user_inp["summary"])
        rec.typ(user_inp["type"])
        rec.tags(user_inp["tags"])
        rec.paymentMethod(user_inp["payment"])
        rec.store()
