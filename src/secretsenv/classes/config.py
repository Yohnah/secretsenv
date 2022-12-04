from pathlib import Path
from .conftemplates import config as config_dict
from .loadinifiles import ReadIniFile
from configparser import ConfigParser
from .exceptions import NotAttributesWereSet, FileNotFound, AttributeNotSet, BadFormatName, VaultNotSet
import argparse
import os, sys, platform

class config(object):
    def __init__(self):
        sys.tracebacklimit = 0
        verbose = os.environ.get("SECRETSENV_VERBOSE",False)
        if verbose != False:
            self.verbose = True
            sys.tracebacklimit = 20

        args = self.arguments()

        self.conffile = os.environ.get("SECRETSENV_CONFIG_FILE",args.config)
        self.setup()
        if not os.path.exists(self.conffile):
            raise FileNotFound(self.conffile)
        
        
        vaults_file = os.environ.get("SECRETSENV_VAULTS_FILE",args.vaults_file)
        if not vaults_file is None:
            self.vaults_file = vaults_file

        profiles_dir = os.environ.get("SECRETSENV_PROFILES_DIR",args.profiles_dir)
        if not profiles_dir is None:
            self.profiles_dir = profiles_dir
 
        if not args.ssh is None:
            self.ssh = True if args.ssh == 'True' else False

        if not args.ssh_agent_type is None:
            self.ssh_agent_type = args.ssh_agent_type

        if not args.ssh_agent_path is None:
            self.ssh_agent_path = args.ssh_agent_path

        if (self.vaults_file is None):
            raise NotAttributesWereSet()

        self.action = args.action

        self.operative_system = platform.system().lower()

        self.profile_file = args.profile        
        if (args.profile.find("/") < 0):
            if self.profiles_dir is None:
                raise AttributeNotSet("PROFILE")

            profile = args.profile
            if profile.find(".secrets") < 0:
                profile = profile+".secrets"
            self.profile_file = self.profiles_dir.rstrip('/')+"/"+profile

        self.profile_section = args.profile_section.lower()

        if self.action == "run":
            self.command = args.command

        if self.action == "dump":
            self.format = args.format
    
    @property
    def vaults(self):
        return self.loadConf(self.vaults_file)

    @property
    def vaults_to_use(self):
        get_vault = lambda value: value['vault'].lower()
        result = list(map(get_vault,self.profile.values()))
        return list(set(result)) #return unique vault names from profile list

    @property
    def profile(self):
        result = {}
        for key,value in self.loadConf(self.profile_file).get(self.profile_section,None).items():
            try:
                type_of_variable,name_of_variable = key.split('@')
            except:
                raise BadFormatName(key)

            splitted_value = value.split(":")

            vault = splitted_value[0].lower()
            if not vault in self.vaults.keys():
                raise VaultNotSet(vault)

            result[name_of_variable] = {
                "type" : type_of_variable.lower(),
                "query": ":".join(splitted_value[1:]),
                "vault": splitted_value[0].lower()
            }

        return result

    def loadConf(self,inifile):
        if not os.path.exists(inifile):
            raise FileNotFound(inifile)
        readinifile = ReadIniFile(inifile)
        return readinifile.content

    def setup(self):
        if not os.path.isfile(self.conffile):
            f = Path(self.conffile)
            f.touch(exist_ok=True)
            conf = ConfigParser()
            conf.read_dict(config_dict)
            with open(self.conffile, 'w') as configfile:
                conf.write(configfile)
        
        config = self.loadConf(self.conffile)

        if "config" in config:
            self.ssh = True if config['config'].get('ssh','True') == 'True' else False
            self.ssh_agent_type = config['config'].get('ssh_agent_type',None)
            self.ssh_agent_path = config['config'].get('ssh_agent_path',None)
            self.vaults_file = config['config'].get('vaults_file',None)
            self.profiles_dir = config['config'].get('profiles_dir',None)


    def arguments(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,description='Tool for raising a configured shell with all required secrets, retrieved from compatible vaults, for your project onto memory in user space',epilog="♬♬♪ Secret is in the env... ♪♬♬")
        parser.add_argument("--config", "-c", default=Path.home()/".secretsenv.conf",help="Set Secrets to env manifest file path or set SECRETSENV_CONFIG_FILE environment variable: Default: %(conffile)s" % {'conffile': Path.home()/".secretsenv.conf"})
        parser.add_argument("--vaults_file", "-vf", default=None,help="Set Vaults settings definitions. Also, set \"vaults_file\" attribute into config file or set SECRETSENV_VAULTS_FILE environment variable.")
        parser.add_argument("--profiles_dir", "-pd", default=None,help="Set profile directory where profiles files (with suffix \".secrets\") will be stored. Also, set \"profiles_dir\" attribute into config file or set SECRETSENV_PROFILES_DIR environment variable. Default: None")
        parser.add_argument("--ssh",choices=["True","False"], default=None,help="Add private ssh keys to ssh-agent or pageant")
        parser.add_argument("--ssh_agent_type",choices=["ssh-agent","pageant"],default="ssh-agent",help="Set SSH-AGENT or PageAnt to be used to load private ssh keys. Also, set \"ssh_agent_type\" within config file. Defaults: ssh-agent")
        parser.add_argument("--ssh_agent_path",default=None,help="Set SSH-AGENT or PageAnt to be used to load private ssh keys. Also, set \"ssh_agent_path\" within config file. Defaults: None")
        parser.add_argument("profile", help="Set the profile name stored within \"profiles_dir\" or file path")
        parser.add_argument("profile_section", help="Set the section to load the defined variables within profile file")
        subparsers = parser.add_subparsers(dest='action', help='Choose once of the following actions:')
        subparsers.required = True
        run_parser = subparsers.add_parser('run', help='Running a command and set the secrets into command running space')
        run_parser.add_argument("command", help="Set a command to run. Example: $ secretsenv profile run /bin/bash")
        show_parser = subparsers.add_parser('dump', help='Dump secrets in screen')
        show_parser.add_argument("format", default="table", choices=["powershell_shell","cmd_shell","unix_shell","table","json"], help="Choose the format to show secrets in screen")
        args = parser.parse_args()
        return args