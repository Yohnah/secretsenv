from asyncio import subprocess
from pathlib import Path
from ..classes import exception
import configparser
import profile
import sys, os, shutil, glob
from ..modules.keepass import keepass as KeePassClass
from ..modules.sshagent import SshAgent
import subprocess,platform,re,traceback,json

sys.tracebacklimit = 5

class Setup (object):
    def __init__(self) -> None:
        self.operative_system = platform.system().lower()
        if self.operative_system == "windows":
            confdir_path = os.environ.get("SECRETSENV_CONFDIR",Path.home()/".secretsenv")
            self.confdir_path = str(confdir_path).lower()
        else:
            self.confdir_path = os.environ.get("SECRETSENV_CONFDIR",Path.home()/".secretsenv")

        self.configini_file = str(self.confdir_path)+"/config.ini"
        self.profiles_dir = str(self.confdir_path)+"/profiles"
        path = Path(os.path.dirname(__file__))
        self.appdir = path.parent.absolute()
        self.template_dir = self.appdir / "templates"
    
    def init(self) -> None:
        os.makedirs(self.confdir_path, exist_ok=True)
        os.makedirs(self.profiles_dir, exist_ok=True)
        shutil.copyfile(str(self.template_dir)+"/config.ini",self.configini_file)
        print("Confdir created at %(confdir)s" % {'confdir': self.confdir_path})



class ParseIniFile (object):

    def __init__(self,conffiles:list=None) -> None:
        self.content = {}
        self.confs = {}
        self.conffiles = conffiles
        self.loadfiles()
        self.parser()

    def loadfiles(self):
        for conffile in self.conffiles:
            try:
                config = configparser.ConfigParser()
                config.optionxform=str
                config.read(conffile)
            except configparser.DuplicateSectionError as error:
                print("Error:\r\n\r\nFile %(conffile)s is empty. Created example file" % {"conffile": conffile},file=sys.stderr)
                exit(1)
            self.confs[conffile] = config

    def parser(self):
        for conf in self.confs:
            self.content[conf] = {}
            for section in self.confs[conf.lower()].sections():
                self.content[conf.lower()][section.lower()] = dict(self.confs[conf.lower()].items(section))


                
class LoadConfigIni(ParseIniFile):
    def parser(self):
        super().parser()
        self.content=list(self.content.values())[0]
            

class LoadProfileIni(ParseIniFile):
    def __init__(self,profiles_dir:str,profile,query=None) -> None:
        files = glob.glob(profiles_dir+"/*.ini")
        self.profile = profile
        self.query = query
        super().__init__(files)
    
    def parser(self):
        content = {}
        splitted=self.profile.split(".")
        profile=splitted[0]
        query = self.query
        if len(splitted) == 2:
            query = splitted[1]
        super().parser()
        for conf in self.content:
            info = self.content[conf]['info']
            if info['profile'] != profile:
                continue
            del self.content[conf]['info']
            content[info['profile']] = {}
            for section in self.content[conf]:
                if section != query:
                    continue
                content[info['profile']][section] = {}
                for secret in self.content[conf][section]:
                    backend,query = self.content[conf][section][secret].split(";")
                    content[info['profile']][section][secret] = {
                        'backend' : backend,
                        'query': query
                    }
        self.content = content

class LoadSecretsManifest(ParseIniFile):
    def __init__(self,files:list,section) -> None:
        self.section = section
        super().__init__(files)

    def parser(self):
        content = {}
        super().parser()
        for conf in self.content:
            info = self.content[conf]['info']
            del self.content[conf]['info']
            content[info['profile']] = {}
            for section in self.content[conf]:
                if section != self.section:
                    continue
                content[info['profile']][section] = self.content[conf][section]
                for secret in self.content[conf][section]:
                    engine = self.content[conf][section][secret]
                    content[info['profile']][section][secret] = {
                        "engine" : engine,
                    }
        self.content = content


def backendsParser (backend_name,backendConf) -> None:
        result = {}
        records = backendConf[backend_name].copy()  
        for record in records:
            try:
                backend,query = records[record].split(";")
                backend = backend.lower()
                subresult = backendsParser(backend,backendConf)
                records['password'] = subresult[backend].query(query)
                result.update(subresult)
            except:
                pass

        if not backend_name in result:
            if records['type'].lower() == 'keepass':
                result[backend_name] = KeePassClass(backend_name,**records)

        return result


class Dump (object):
    def __init__(self,profile,section,secrets):
        self.profile = profile
        self.section = section
        self.secrets = secrets

    def print(self,type,secret=None):
        if type == 'table':
            self.table(secret)
        if type == 'ssh_keys':
            self.ssh_keys(secret)
        if type == 'unix_shell':
            self.unix_shell(secret)
        if type == 'cmd_shell':
            self.cmd_shell(secret)
        if type == 'powershell_shell':
            self.powershell_shell(secret)
        if type == 'json':
            self.json(secret)
    
    def json(self,secret):
        print(json.dumps(self.secrets))

    def powershell_shell(self,secret_name):
        variables = ""
        if secret_name == None:
            for secret in self.secrets:
                if self.secrets[secret]['engine'] == 'variable':
                    variables += "$env:%(secret)s = '%(content)s' \r\n" % {"secret": secret, "content": self.secrets[secret]['content']}
        else:
            if self.secrets[secret_name]['engine'] == 'variable':
                variables += "$env:%(secret)s = '%(content)s' \r\n" % {"secret": secret_name, "content": self.secrets[secret_name]['content']}

        dump = "$env:PROFILE = '{profile}'\r\n" \
        + "$env:SECTION = '{section}'\r\n" \
        + variables \

        print(dump.format(profile=self.profile,section=self.section))


    def unix_shell(self,secret_name):
        variables = ""
        if secret_name == None:
            for secret in self.secrets:
                if self.secrets[secret]['engine'] == 'variable':
                    variables += "export %(secret)s=%(content)s \r\n" % {"secret": secret, "content": self.secrets[secret]['content']}
        else:
            if self.secrets[secret_name]['engine'] == 'variable':
                variables += "export %(secret)s=%(content)s \r\n" % {"secret": secret_name, "content": self.secrets[secret_name]['content']}

        dump = "export PROFILE={profile}\r\n" \
        + "export SECTION={section}\r\n" \
        + variables \

        print(dump.format(profile=self.profile,section=self.section))

    def cmd_shell(self,secret_name):
        variables = ""
        if secret_name == None:
            for secret in self.secrets:
                if self.secrets[secret]['engine'] == 'variable':
                    variables += "set %(secret)s=%(content)s \r\n" % {"secret": secret, "content": self.secrets[secret]['content']}
        else:
            if self.secrets[secret_name]['engine'] == 'variable':
                variables += "set %(secret)s=%(content)s \r\n" % {"secret": secret_name, "content": self.secrets[secret_name]['content']}

        dump = "set PROFILE={profile}\r\n" \
        + "set SECTION={section}\r\n" \
        + variables \

        print(dump.format(profile=self.profile,section=self.section))

    def table(self,secret_name):
        variables = ""
        if secret_name == None:
            for secret in self.secrets:
                if self.secrets[secret]['engine'] == 'variable':
                    variables += "- %(secret)s: %(content)s \r\n" % {"secret": secret, "content": self.secrets[secret]['content']}
        else:
            if self.secrets[secret_name]['engine'] == 'variable':
                variables += "- %(secret)s: %(content)s \r\n" % {"secret": secret_name, "content": self.secrets[secret_name]['content']}

        dump = "\r\nProfile: {profile} Section: {section}\r\n" \
        + "=====================================================\r\n" \
        + variables+"\r\n" \

        print(dump.format(profile=self.profile,section=self.section))

    def ssh_keys(self,secret_name):
        if secret_name == None:
            for secret in self.secrets:
                if self.secrets[secret]['engine'] == 'ssh':
                    print (self.secrets[secret]['content'])
        else:
            if self.secrets[secret_name]['engine'] == 'ssh':
                print (self.secrets[secret_name]['content'])

class Run (object):
    def __init__(self,profile,section,secrets):
        self.profile = profile
        self.section = section
        self.secrets = secrets

    def ssh_agent_parse_env(self,output):
        result = {}
        for name, value in re.findall(r'([A-Z_]+)=([^;]+);', output.decode('ascii')):
            result[name] = value
        return result

    def run(self,command):
        env = os.environ.copy()
        banner = "\r\nProfile \"%(profile)s\" with \"%(section)s\" section loaded\r\n" % {'profile': self.profile,'section':self.section} \
        + "***************************************************"
        print(banner)

        setup = Setup()
        if setup.operative_system.lower() == 'windows':
            pass
        else:
            ssh = SshAgent()
        
        for secret in self.secrets:
            if self.secrets[secret]['engine'] == 'variable':
                env[secret] = self.secrets[secret]['content']
            if self.secrets[secret]['engine'] == 'ssh':
                print("Adding SSH Key "+secret)
                ssh.add_key(self.secrets[secret]['content'])

        env.update(ssh.environment)        

        print('\r\n')
        subprocess.run(command,shell=True,env=env)

        banner = "\r\nRemoving session of profile \"%(profile)s\"" % {'profile': self.profile}
        print(banner)



