class ExceptionBase(Exception):
    pass

class NotProfileExist (Exception):
    def __init__(self,profile):
        message = "\r\n\r\nProfile <<%(profile)s>> not found within profiles directory" % {'profile':profile}
        super().__init__(message)

class NotSecretExist (Exception):
    def __init__(self,secret):
        message = "\r\n\r\nSecret definition <<%(secret)s>> not found within any profile" % {'secret':secret}
        super().__init__(message)

class backendNotFound (Exception):
    def __init__(self,backends):
        message = "\r\n\r\nThe following backends definitions were not found in the config file: %(backends)s" % {'backends': ", ".join(backends) }
        super().__init__(message)

class methodNotSet (Exception):
    def __init__(self,method):
        message = "\r\n\r\nThe method <<%(method)s>>" % {'method': method }
        super().__init__(message)