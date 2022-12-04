from modules.keepass import keepass as KEEPASS
from classes.exceptions import VaultNotSet
import getpass

class vaults (object):
    def __init__(self,config) -> None:
        self.__connections = {}
        
        vaults_list = config.vaults_to_use

        while len(vaults_list) > 0:
            vault_name = vaults_list.pop()
            vault_settings = config.vaults.get(vault_name.lower())
            connection = self.__connection_parser(vault_name,vault_settings)
            if not connection is None:
                self.__connections[vault_name] = connection
            
            if connection is None:
                vaults_list.append(vault_name)
                vaults_list.reverse() #the new appended element is the first element to pop, so, to reverse it is necesary to rotate the elements


    def __connection_parser(self,vault_name,settings):
        if settings is None:
            raise VaultNotSet(vault_name)
        
        settings_data = {}
        for field,value in settings.items():
            if value.lower() == "prompt":
                value = getpass.getpass(f"Vault {vault_name.capitalize()} - Set {field.capitalize()} value: ")
            
            splitted_value = value.split(":")
            if (len(splitted_value) > 1) and (len(splitted_value[0]) > 1):
                calling_vault = splitted_value[0].lower()
                if calling_vault in list(self.__connections.keys()):
                    query = ":".join(splitted_value[1:])
                    value = self.__connections[calling_vault].query(query)
                else:
                    return None
            settings_data[field] = value


        if settings_data["type"] == "keepass":
            return KEEPASS(**settings_data)
        
        return None


    def __getitem__(self, name):
        return self.__connections[name]
    
    def __setitem__(self,name,value):
        self.__connections[name] = value

    def __iter__(self):
        dct = self.__connections.copy()
        return iter(dct)


