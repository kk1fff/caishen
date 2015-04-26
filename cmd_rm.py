class RemoveCommand:
    def __init__(self, csb):
        self._csb = csb

    def run(self, argv):
        if len(argv) < 1:
            raise Exception("ID isn't specified")

        recId = argv[0]
        rec = self._csb.findById(recId)
        if rec == None:
            raise Exception("ID {} is not found.".format(recId))
        rec.delete()
        print("Record {} deleted".format(recId))
