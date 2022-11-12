import argparse

class Arguments(object):
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,description='Tool for raising a configured shell with all required secrets, retrieved from compatible vaults, for your project onto memory in user space',epilog="♬♬♪ Secret is in the env... ♪♬♬")
        self.parser.add_argument("--secretstoenv_file", default="./secretstoenv.ini", help="Set Secrets to env manifest file path. Default: ./secretstoenv.ini")
        subparsers = self.parser.add_subparsers(dest='action', help='Choose once of the following actions:')
        init_parser = subparsers.add_parser('init', help='To create the config directory at $HOME/.secretsenv')
        run_parser = subparsers.add_parser('run', help='Running a command and set the secrets into command running space')
        run_parser.add_argument("section", help="Set the section from reading the specific secrets.")
        run_parser.add_argument("command", help="Set a command to be run. Example: $ secretsenv run profile /bin/bash")
        show_parser = subparsers.add_parser('dump', help='Dump secrets in screen')
        show_parser.add_argument("section", help="Set the section from reading the specific secrets.")
        show_parser.add_argument("--format", default="table", choices=["powershell_shell","cmd_shell","unix_shell","table","json","ssh_keys"], help="Choose the format to show secrets in screen")
        show_parser.add_argument("--secret", help="Get the secret to dump")
        self.args = self.parser.parse_args()



