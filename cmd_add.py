from user_input import getUserInput

class AddCommand:
    def __init__(self, csbook):
        self._csb = csbook

    def run(self, args):
        rec = self._csb.makeRecord(getUserInput(self._csb))
        rec.store()
