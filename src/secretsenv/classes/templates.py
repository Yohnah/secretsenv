from ..classes import exception

class backend (object):
    def __init__(self,backend_name,**options):
        self.options = options
        self.backend_name = backend_name
        self.load()

    def load(self):
        raise exception.methodNotSet("load")

    def query(self):
        raise exception.methodNotSet("query")