from ..classes import templates, exception
from pykeepass import PyKeePass, exceptions
import getpass

class KeePassDBnotSet(exception.ExceptionBase):
    pass
    
class KeePassRecordNotFound(exception.ExceptionBase):
    pass

class KeePassBadQueryFormat(exception.ExceptionBase):
    pass

class keepass (templates.backend):
    def load (self):
        db_path = self.options.get('db_path',None)
        if db_path == None:
            raise KeePassDBnotSet("db_path not set")

        
        if (self.options.get('password',"false") == "true"):
            password = getpass.getpass("Password for %(backend_name)s backend: " % {'backend_name': self.backend_name})
        else:
            password = self.options.get('password')
        
        keyfile = self.options.get('keyfile',None)
        self.connection = PyKeePass(db_path,password=password,keyfile=keyfile)

    def query(self,query):
        # /path/to/record#field:name or /path/to/record#attach:name

        try:
            path,record = query.split('#')
            type_of_record,name_of_type_of_record = record.split(':')
            array_path = path.split('/')
        except:
            print ("Please, set the query such as /path/to/record#field:name_of_file, /path/to/record#attach:name_of_attachment")

        result = self.connection.find_entries(path=array_path[1:],regex=True,first=True)
        
        if type_of_record == 'attach':
            for attach in result.attachments:
                if attach.filename == name_of_type_of_record:
                    return attach.data.decode('ascii')
        
        if type_of_record == 'field':
            for field in result._get_string_field_keys():
                if field.lower() == name_of_type_of_record.lower():
                    return result._get_string_field(field)
        
        raise KeePassRecordNotFound('The record or value of %(query)s was not found in KeePass DB' % {'query': query})

