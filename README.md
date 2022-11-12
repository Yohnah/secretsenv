<div align="center">
♬♬♪ Secret is in the env, everywhere I look around    ♪♬♬ <br/>
♪♬♪ Secret is in the env, every token and every vault ♪♬♪ <br/>
♪♪♬ And I don't know if I'm being foolish             ♬♬♪ <br/>
♪♪♪ Don't know if I'm being wise                      ♬♪♬ <br/>
♬♪♪ But it's something that I must have in            ♬♬♬ <br/>
♬♬♪ And it's there when I avoid in my file             ♬♬♪ <br/>
</div>

# Secrets in the env

Welcome to this simple project, an application launcher to load your secrets in environment variables or SSH private keys into your system's SSH agent, stored in a compatible vault

# To-Do

* Add support for running on Windows
* Add Hashicorp Vault as a vault compatible

# Requirements

## Compatible Operative Systems as host

* MacOS (tested on BigSur x86_64 and higher)
* GNU/Linux
___
***Note:***
Windows is not already compatible because some pykeepass issues on Windows. I'm working on fixing it.
___

## Software

* Python 3: <https://www.python.org/>
  * Dependences:
    * PyKeePass: https://github.com/libkeepass/pykeepass

# Current compatible vaults

* KeePaas 2: <https://keepass.info/>

# How to use

## Install

Install on Unix-Like and MacOS:

~~~
$ sudo pip install secretsintheenv
~~~

## Help

Just run:

~~~
$ secretsintheenv -h
~~~

Or with any position arguments, ex:

~~~
$ secretsintheenv init -h
$ secretsintheenv run -h
$ secretsintheenv dump -h
~~~

To get a list of arguments and options


## Set-Up

First of all, you have to initialize your profile configuration, such as:

~~~
$ secretsintheenv init
~~~

And, you will get a new created directory at $HOME/.secretsenv/ as follow:

~~~
$HOME/.secretsenv
├── config.ini  #File to setup your compatible vault
└── profiles/   #Directory to store different profile files to match variables with stored secrets in compatible vaults
~~~

## Step 1

Configure the vault types needed to be referenced by the different manifests (see next steps).
___
***Note:***
At the moment only KeePass is supported
___

To configure the list of available vaults you must edit the file $HOME/.secretsenv/config.ini with content like the following:

~~~
[head_vault]
type=keepass
db_path=/path/of/keepass/file.kdbx
password=true
keyfile=/path/to/private/key/file.key 

[KEEPASS_1]
type=keepass
db_path=/path/of/keepass/file2.kdbx
password=head_vault;/path/to/record/to/retrieve/pass#field:field_name

[KEEPASS_2]
type=keepass
db_path=/path/of/keepass/file3.kdbx
password=head_vault;/path/to/record/to/retrieve/pass#field:field_name
keyfile=/path/to/private/key/file3.key 
~~~

Each vault configuration must be defined from a section of the type [backend_name_1], using the name of your choice (the name is case insensitive).

Next, each section must necessarily have the type argument with one of the following values defined:

 * keepass
___
***Note:***
At the moment only vault KeePass is supported
___

Following the arguments needed by the vault itself to work

Following the arguments needed by the vault itself to work. Below we list the arguments needed by vault compatible:

### KeePaas

* type=keepass (Mandatory)
* db_path=/path/to/keepass/file.kdbx (Mandatory)
* password (optional)
  * Password can either have the value "true", which will cause you to be prompted for the password, or it can have a "plain string" that will be used as the password. Ex:
    * password=true
    * password=<<password>>
* keyfile=/path/to/keepass/file.key (optional)

***Look Out!***
If you write a password in the password attribute, the password is stored in clear, which is dangerous because anyone with access to the file will be able to retrieve all the secrets from the vault.

To avoid this, you can create another vault to be used as "head vault", for example, another keepass, which stores the passwords of the rest of the vaults and the password attribute is set to "true".

In the rest of the vaults you can reference the content of the password with the following format, ex:

~~~
[...]
password=backend_name;query_to_retrieve_the_secret
[...]
~~~
___
***Note:***
For futher informartion of the type of query to be used, see the step 3
___

In this way, the "head vault" will prompt for a password to retrieve the secrets to unlock of rest of vaults.

## Step 2

Create a manifest file in your work directory with the name "secretstoenv.ini". 

This file will content the profile manifest to list the differents type of data to be load among different sections.

An example of file could be:

~~~
[Info]
profile=profile_name

[PROD]
GITHUB_TOKEN=variable
AWS_ACCESS_KEY_ID=variable
AWS_SECRET_ACCESS_KEY=variable
SSH_KEY=ssh

[QUA]
GITHUB_TOKEN=variable
AWS_ACCESS_KEY_ID=variable
AWS_SECRET_ACCESS_KEY=variable
ANY_VARIABLE_NAME=ssh
ANY_VARIABLE_NAME_1=ssh
ANY_VARIABLE_NAME_2=variable

[DEV]
GITHUB_TOKEN=variable
AWS_ACCESS_KEY_ID=variable
AWS_SECRET_ACCESS_KEY=variable
ANY_VARIABLE_NAME=ssh
VARIABLE_TO_BE_USED_ON_DEV=ssh
~~~

Sections are defined as [section_name] and are case insensitive. They can be defined by any name you prefer.

Each section contains a set of variables or ssh keys to be loaded.

The only mandatory section should be [Info], which indicates the name of the profile to be used, such as:

**profile**=*profile_name*

The variables are defined as follows:

**VARIABLE_NAME**=**type_of_variable** #It's case sensitive

**VARIABLE_NAME** is the name of the variable that will be used as environment variable and **type_of_variable** can be set with the following values:

* __variables__. Which indicates that this secret will be an environment variable
* __ssh__. Which indicates that this secret is an SSH private key that must be inserted in the SSH-Agent service

___
***Note:***
The definition of variables is case sensitive because the variable name format requested by the application that needs to consume the secret must be respected
___

***Note:***
The idea of this manifest is to be stored in the working directory of the project you are developing. In this way, it is useful to load the secrets in memory in an ephemeral and easy way, in addition to having a declaration of the secrets that the project needs and the type of secret as part of the project documentation.

For example, as part of a project developed in a Git repository
___

## Step 3

Create a file in the following directory $HOME/.secretsenv/profiles/ (one file per profile).

The content of this file is exactly the same as the secretstoenv.ini manifest in your working directory, but instead of indicating the type of variable (whether environment variables or SSH keys), the backend to query must be defined and the query to be execute, such as:

**VARIABLE_NAME**=*backend_name*;query

Example:
~~~
[Info]
profile=profile_name

[PROD]
GITHUB_TOKEN=KEEPASS_2;/path/to/record#field:field_name
AWS_ACCESS_KEY_ID=KEEPASS_2;/path/to/record2#field:field_name
AWS_SECRET_ACCESS_KEY=KEEPASS_1;/path/to/record3#field:field_name
SSH_KEY=KEEPASS_2;/path/to/record4#attach:attachment_name

[QUA]
GITHUB_TOKEN=KEEPASS_1;/path/to/record20#field:field_name
AWS_ACCESS_KEY_ID=KEEPASS_2;/path/to/record12#field:field_name
AWS_SECRET_ACCESS_KEY=KEEPASS_2;/path/to/record#field1:field_name
ANY_VARIABLE_NAME=KEEPASS_1;/path/to/record13#attach:attachment_name
ANY_VARIABLE_NAME_1=KEEPASS_2;;/path/to/record4#field:field_name
ANY_VARIABLE_NAME_2=KEEPASS_2;/path/to/record3#field:field_name

[DEV]
GITHUB_TOKEN=KEEPASS_1;/path/to/record53#field:field_name
AWS_ACCESS_KEY_ID=KEEPASS_1;/path/to/record27#field:field_name
AWS_SECRET_ACCESS_KEY=KEEPASS_2;/path/to/record33#field:field_name
ANY_VARIABLE_NAME=KEEPASS_1;/path/to/record45#field:field_name
VARIABLE_TO_BE_USED_ON_DEV=KEEPASS_2;/path/to/record12#field:field_name
~~~

### Queries type

#### keepass

KeePass queries adhere to the following format:

/path/to/record/to/retrieve#record_type:record_name

Where:

* **/path/to/registry/to/retire** is the path to the registry where the secret is stored in the KeePass database

* **record_type** can get the following values:
  * **field**. To indicate to KeePass that the secret is stored in a field
  * **attach**. To indicate to KeePass that the secret is stored as an attachment.
* **record_name**. The name of field or attachment where is stored the secret

## Step 4

Just use it!

### Dumping data

In order to dump data just run:

~~~
$ secretsintheenv dump <section>
~~~

Where section are the defined sections in manifest files. In our example would be PROD, QUA and DEV

Ex for dumping secrets 

* table format
~~~
$ secretsintheenv dump prod
~~~

or

~~~
secretsintheenv dump prod --format table
~~~

* powershell style
  
~~~
secretsintheenv dump prod --format powershell_shell
~~~

* cmd style

~~~
secretsintheenv dump prod --format cmd_shell
~~~

* unix_shell style

~~~
secretsintheenv dump prod --format unix_shell
~~~

* json

~~~
secretsintheenv dump prod --format json
~~~

* ssh_keys

~~~
secretsintheenv dump prod --format ssh_keys
~~~

### Running a command

Use the format:

~~~
$ secretsintheenv run <section> <command>
~~~

Where \<section\> are the defined sections in manifest files. In our example would be PROD, QUA and DEV, and \<command\> the command to execute and load the secrets

For example:

~~~
$ secretsintheenv run qua /bin/bash
~~~

It will execute an interactive bash shell by loading the secrets defined in QUA section as environment variables and SSH keys into the SSH-Agent

All secrets are ephimerals, so, once the command ends, all secrets are removed from the memory.