import subprocess,re,os

class SshAgent (object):
    def __init__(self):
        self.environment = os.environ.copy()
        self.agent_output = subprocess.check_output(['ssh-agent', '-s'])
        agent_env = self.ssh_agent_parse_env()
        self.environment.update(agent_env)

    def ssh_agent_parse_env(self):
        result = {}
        for name, value in re.findall(r'([A-Z_]+)=([^;]+);', self.agent_output.decode('ascii')):
            result[name] = value
        return result


    def add_key(self,key):
        subprocess.run('echo "'+key+'" | ssh-add -', shell=True, env=self.environment)