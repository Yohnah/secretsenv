from classes.config import config as CONFIG
from classes.vaults import vaults as VAULTS
from classes.dump import dump as DUMP
from classes.run import run as RUN

secrets = {}

def main():
    config = CONFIG()
    vaults = VAULTS(config)

    for variable_name, settings in config.profile.items():
        secrets[variable_name] = {
            "type": settings['type'],
            "content": vaults[settings['vault']].query(settings['query'])
        }

    if config.action == "dump":
        dump = DUMP(config,secrets)
    
    if config.action == "run":
        drun = RUN(config,secrets)
    

if __name__ == "__main__":
    main()