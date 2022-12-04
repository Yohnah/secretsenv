import json

class dump(object):
    def __init__(self,config,secrets) -> None:
        self.result = secrets
        self.config = config

        if self.config.format == "table":
            self.table()
        if self.config.format == "json":
            self.json()
        if self.config.format == "unix_shell":
            self.unix_shell()
        if self.config.format == "powershell_shell":
            self.powershell_shell()
        if self.config.format == "cmd_shell":
            self.cmd_shell()

    def table(self):
        print ("")
        header = f"Profile: {self.config.profile_file} - Section: {self.config.profile_section}"
        print (header)
        print(f"="*len(header))
        for key,value in self.result.items():
            print(key+" - type: "+value['type'])
            print(f"-"*len(key+" - type: "+value['type']))
            print(value['content'])
            print("")
        #print(self.result)
        print("")

    def json(self):
        print(json.dumps(self.result,indent=3))

    def unix_shell(self):
        for key,value in self.result.items():
            if value['type'].strip() == 'var':
                print(f"export {key}={value['content']}")

    def powershell_shell(self):
        for key,value in self.result.items():
            if value['type'].strip() == 'var':
                print(f"$env:{key} = {value['content']}")

    def cmd_shell(self):
        for key,value in self.result.items():
            if value['type'].strip() == 'var':
                print(f"set {key}={value['content']}")