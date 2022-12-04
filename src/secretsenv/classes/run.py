import os, subprocess, re, tempfile
from ..classes.tools import delete_file

class SshAgent (object):
    def __init__(self,ssh_agent_path=None,new_process=True):
        self.environment = os.environ.copy()
        if ssh_agent_path == None:
            ssh_agent_path = 'ssh-agent'
        self.agent_output = subprocess.check_output([ssh_agent_path, '-s'])
        agent_env = self.ssh_agent_parse_env()
        self.environment.update(agent_env)

    def ssh_agent_parse_env(self):
        result = {}
        for name, value in re.findall(r'([A-Z_]+)=([^;]+);', self.agent_output.decode('ascii')):
            result[name] = value
        return result


    def add_key(self,key):
        with tempfile.NamedTemporaryFile(mode="wt",delete=False) as key_tmp:
            key_tmp.write(key)
            key_name = key_tmp.name
        subprocess.run(f"ssh-add {key_name}", shell=True, env=self.environment)

        delete_file(key_name)

    def del_keys(self):
        subprocess.run("ssh-add -D", shell=True, env=self.environment)

class run (object):
    def __init__(self,config,secrets) -> None:
        self.config = config
        self.secrets = secrets
        self.environment = os.environ.copy()

        if (config.ssh == True) and (config.ssh_agent_type == "ssh-agent"):
            ssh_agent_path = config.ssh_agent_path
            ssh_agent_new_process = True
            if config.operative_system == 'windows':
                ssh_agent_path = None #Call ssh-agent from environment PATH variable on Windows
                ssh_agent_new_process = False

            ssh = SshAgent(ssh_agent_path,ssh_agent_new_process)

        for secret,value in self.secrets.items():
            if value['type'] == 'var':
                self.environment[secret] = value['content']
            if (config.ssh == True) and (value['type'] == 'ssh'):
                print(f"Adding SSH Key: {secret}")
                ssh.add_key(value['content'])
        
        self.environment.update(ssh.environment)
        subprocess.run(self.config.command,shell=True,env=self.environment)

        if (config.ssh == True):
            ssh.del_keys()


    
