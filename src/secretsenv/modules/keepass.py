import os
import tempfile

from classes.exceptions import BadFormat, ItisNotaFile
from classes.tools import delete_file
from pykeepass import PyKeePass


class keepass (object):
    class BadFormat (Exception):
        def __init__(self, query) -> None:
            message = f"The format of \"{query}\" is not correct. Please, set the query such as /path/to/record#field:name_of_file or /path/to/record#attach:name_of_attachment"
            super().__init__(message)

    class RecordNotFound (Exception):
        def __init__(self, query, db_path) -> None:
            message = f"The record \"{query}\" was not found is KeePass DB {db_path}"
            super().__init__(message)
     

    def __init__(self,db_path,password=None,keyfile=None,**kwargs) -> None:
        if (type(db_path) != str) or (not os.path.isfile(db_path)):
            raise ItisNotaFile("db_path")
        
        if (password != None) and (type(password) != str):
            raise BadFormat("Password")

        self.key_tmp_name = None
        if (keyfile != None):
            if os.path.isfile(keyfile):
                with open(keyfile,"rb") as key_file:
                    key_content = key_file.read()
                keyfile = key_content
            
            with tempfile.NamedTemporaryFile(delete=False) as key_tmp:
                key_tmp.write(keyfile)
                self.key_tmp_name = key_tmp.name
            

        self.db_path = db_path
        with open(db_path,"rb") as db_content_file:
            db_content = db_content_file.read()

        with tempfile.NamedTemporaryFile(delete=False) as db_tmp:
            db_tmp.write(db_content)
            self.db_tmp_name = db_tmp.name

        self.connection = PyKeePass(self.db_tmp_name,password=password,keyfile=self.key_tmp_name)

    def __del__(self):
        delete_file(self.key_tmp_name)
        delete_file(self.db_tmp_name)

    def query(self,query):
        try:
            path,record = query.split('#')
            type_of_record,name_of_type_of_record = record.split(':')
            array_path = path.split('/')[1:]
        except:
            raise self.BadFormat(query)

        result = self.connection.find_entries(path=array_path,regex=True,first=True)

        if type_of_record == 'attach':
            for attach in result.attachments:
                if attach.filename == name_of_type_of_record:
                    return attach.data.decode('ascii') #comprobar porque está decode ascii

        if type_of_record == 'field':
            for field in result._get_string_field_keys():
                if field.lower() == name_of_type_of_record.lower():
                    return result._get_string_field(field)

        raise self.RecordNotFound(query,self.db_path)