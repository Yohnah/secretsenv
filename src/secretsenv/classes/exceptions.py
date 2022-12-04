class NotAttributesWereSet (Exception):
    def __init__(self):
        message = "Vaults_files must be set"
        super().__init__(message)

class FileNotFound(Exception):
    def __init__(self, file) -> None:
        message = f"File {file} not found"
        super().__init__(message)

class BadFormatInitFile(Exception):
    def __init__(self,file) -> None:
        message = f"Bad INI format in {file}"
        super().__init__(message)

class AttributeNotSet(Exception):
    def __init__(self, attribute) -> None:
        message = f"The {attribute} attribute was not set"
        super().__init__(message)

class VaultNotSet(Exception):
    def __init__(self, vault_name) -> None:
        message = f"The Vault \"{vault_name}\" was not configured within the vault configuration file"
        super().__init__(message)

class ItisNotaFile(Exception):
    def __init__(self, variable_name) -> None:
        message = f"The value of {variable_name} must be a file path"
        super().__init__(message)

class BadFormat(Exception):
    def __init__(self, variable_name) -> None:
        message = f"The value of {variable_name} has a bad format"
        super().__init__(message)

class BadFormatName(Exception):
    def __init__(self, variable_name) -> None:
        message = f"The name of the variable {variable_name} has a bad format. It must be \"VARTYPE@VARNAME\". Allowed VARTYPE values are: VAR for environment variables or SSH for SSH-AGENT contents"
        super().__init__(message)
