#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .classes.core import Setup, LoadConfigIni, LoadSecretsManifest, LoadProfileIni, backendsParser, Dump, Run
from .classes.arguments import Arguments
from .classes import exception
import sys

def main ():
    setup = Setup()
    backends = []

    arguments = Arguments()
    if arguments.args.action == None:
        arguments.parser.print_help()
        sys.exit(1)
    
    if arguments.args.action == "init":
        setup.init()
    
    
    if arguments.args.action == "run" or arguments.args.action == "dump":
        confini = LoadConfigIni([setup.configini_file])
        manifestfile = LoadSecretsManifest([arguments.args.secretstoenv_file],arguments.args.section.lower())
        profile = list(manifestfile.content.keys()).pop()
        section = arguments.args.section.lower()
        profilesini = LoadProfileIni(setup.profiles_dir,profile,section)
        if not profile in profilesini.content.keys():
            raise exception.NotProfileExist(profile)

        secrets = {
            profile : {
                section : {}
            }
        }

        for secret in manifestfile.content[profile][section]:
            if not secret in profilesini.content[profile][section]:
                raise exception.NotSecretExist(secret)
            
            engine = manifestfile.content[profile][section][secret]['engine']
            backend = profilesini.content[profile][section][secret]['backend'].lower()
            query = profilesini.content[profile][section][secret]['query']
            
            secrets[profile][section][secret] = {
                'engine': engine,
                'backend': backend,
                'query': query,
            }

            backends.append(backend) if backend not in backends else backends


        backends_not_found = list(set(backends) - set(list(confini.content.keys())))

        vaultsConnections = {}
        for backend in backends:
            if not backend in vaultsConnections:
                vaultsConnections.update(backendsParser(backend,confini.content))

        for secret in secrets[profile][section]:
            backend = secrets[profile][section][secret]['backend']
            query = secrets[profile][section][secret]['query']
            content = vaultsConnections[backend].query(query)
            secrets[profile][section][secret]['content'] = content

        if len(backends_not_found) > 0:
            raise exception.backendNotFound(backends_not_found)
    
    if arguments.args.action == "dump":
        dump = Dump(profile,section,secrets[profile][section])
        dump.print(arguments.args.format,arguments.args.secret)

    if arguments.args.action == "run":
        run = Run(profile,section,secrets[profile][section])
        run.run(arguments.args.command)

if __name__ == "__main__":
    main()
    sys.exit(0)