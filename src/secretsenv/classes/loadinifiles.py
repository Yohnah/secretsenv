from .exceptions import BadFormatInitFile
import configparser

class ReadIniFile (object):
    def __init__(self,inifile) -> None:
        self.content = {}
        config = configparser.ConfigParser()
        config.optionxform=str
        try:
            config.read(inifile)
        except:
            raise BadFormatInitFile(inifile) from None

        for section in config.sections():
            self.content[section.lower()] = dict(config.items(section))

