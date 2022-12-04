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

* Add Hashicorp Vault as a vault compatible

# Requirements

## Compatible Operative Systems as host

* MacOS (including Chip M1 and M2)
* GNU/Linux
* Windows 10/11/Servers (including SSH-Agent).
  *  For installing OpenSSH on Windows, see https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse?tabs=gui


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
$ pip install secretsintheenv
~~~

On Windows 

**PowerShell**
~~~
PS C:\> pip install secretsintheenv
~~~
**CMD**
~~~
C:\> pip install secretsintheenv
~~~

___
***Note:***
Hereinafter, to run on Windows you should add the .exe suffix to command
Ex:

On Unix-Like:
~~~~
$ ./secretsintheenv -h
~~~~

On Windows:
~~~~
PS C:\> secretsintheenv.exe -h
~~~~
___
***Note:***
In order to run:
~~~
$ secretsintheenv <arguments>
~~~~
~~~
PS C:\> secretsintheenv.exe <arguments>
~~~

It is necessary to install with ADMIN RIGHTS (Using SUDO on Unix-Like or RUNAS on Windows, or similar)

If you install the pip packages with simple users privileges, you have to replace the command above by:

~~~
$  python -m secretsenv.secretsenv <arguments>
~~~
~~~
PS C:\> python.exe -m secretsenv.secretsenv <arguments>
~~~
___

## Help

Just run:

~~~
$ secretsintheenv -h
~~~

## Set-Up

Follow the next steps to reach out a good experience using this tool.

### Step 1

First of all, you have to create your .secretsenv.conf config file on your home directory with the following content:

~~~~
$ cat $HOME/.secretsenv.comf
[Config]
ssh = True
ssh-agent_type = ssh-agent
ssh-agent_path = /usr/bin/ssh-agent
vaults_file = /Path/to/vaults.conf
profiles_dir = /Path/to/profiles/directory/
~~~~

* **ssh** (mandatory): enable or disable SSH-Agent
* **ssh-agent_type** (optional): just suport "ssh-agent" right now
* **ssh-agent_path** (optional): set the path of ssh-agent you prefer using
* **vaults_file** (mandatory): the file path where stored the vaults configurations. Also, it can be replaced by _SECRETSENV_VAULTS_FILE_ environment variable
* **profiles_dir** (optional): the directory path where stored the profile files. Also, it can be replaced by _SECRETSENV_PROFILES_DIR_ environment varaible

___
***Note:***
Attributes can be set or replaced by command lines arguments. ([See Help section](#help))

Line with Hashtags (#) in the beginning are considered comments 
___
***Note:***
The .secretsenv.conf file and path can be replaced by using SECRETSENV_CONFIG_FILE environment variable. If you prefer using your own file, bear in mind to replace .secretsenv.conf by yours until the rest of this README.
___


### Step 2

Once configured the .secretsenv.conf, the next step is to create the vaults file configuration in the path set within .secretsenv.conf

~~~
$ cat /Path/to/vaults.conf
[Section_Name]
type=<type of vault>
<attribute1>=<choose action>
<attribute2>=<choose action>
<attribute3>=<choose action>
[...]
~~~

*  **[Section_Name]** (mandatory, Case Insensitive): Start a new section into file. Section_Name can be any name as you prefer, but it must be unique.
*  **type** (manddatory, Case sensitive): Set the type of vault to be used. ([See the Vaults section](#vaults))
*  **attribute** (case sensitive): The specific attribute to setup the specific vault. 
   *  The type of attribute depends on the vault to configure [See the Vaults section](#vaults) for further information. 
   *  The \<choose action\> value can be the following:
      *  _prompt_. To prompt in the screen and write the value 
      *  _VAULT_NAME:QUERYSTR_. To get the value from another vault. _VAULT_NAME_ is the name of vault to be used set as [Section_Name] and _QUERYSTR_ is the query string to retrieve the expected value. 

You can write as many sections as you need, but remember not to repeat the name of the sections.

___
***Note:***
To see exampled, please visit the section [Examples](#examples)
___


### Step 3
So, we only need one file more (at least). We need to define the profile file (or several) to create the specific querys to retrieve our loved secrets.

The file can be named as you prefer, but it must include the suffix .secrets to work, and a content such as:

~~~
$ cat /Path/to/profiles/directory/PROFILE_NAME.secrets
[Section_Name]
<TYPE>@<TAGNAME1>=<VAULT_NAME1>:<QUERYSTR>
<TYPE>@<TAGNAME2>=<VAULT_NAME2>:<QUERYSTR>
<TYPE>@<TAGNAME3>=<VAULT_NAME3>:<QUERYSTR>
[...]
~~~

Similar to Vaults configuration file, you can define different sections by using the name you prefer, but unique by file, and then, set the different secrets you need to retrieve from specific vault. 

___
***Note:***
The sections can be defined as you prefer, but one way to use it can be to define different work environments (Prod, Qua, Stage, Dev, ...) and thus obtain the different secrets that your project requires at all times
___

* **\<TYPE\>**: Can be:
  * _VAR_: To retrieve the secret such as environment variable
  * _SSH_: To add the secret into SSH-AGENT running in your system
* **\<TAGNAME\>**: The name to identify the retrieved secret. When _VAR_ is used, the TAGNAME will be the environment variable name
* **\<VAULT_NAME\>**: The vault name configured into vault configuration file
* **\<QUERYSTR\>**: The query string (specific by type of vault) to retrieve the secret


## Just run

Once all requirements are configured, just use the tool as follows:

~~~
$ secretsintheenv profile profile_section action command
~~~

* **profile**: If not a path is set to a file, the tool will find your file into the "\<profiles_dir\>/<profile>.secrets" configured into the .secretsenv.conf file
* **profile_section**: To indicate the secrets to be retrieved written in the specific section within the profile file
* **action**: 
  * _run_: to run the command set in the "command" argument
  * _dump_: to dump on screen the secrets content by the format set in the "command" argument



## Examples

Assuming the following configured files:

~~~
 $ cat $HOME/.secretsenv.conf
 [Config]
 ssh = True
 #ssh-agent_type = ssh-agent
 #ssh-agent_path = /usr/bin/ssh-agent
 vaults_file = /Path/to/vaults.conf
 profiles_dir = /Path/to/profiles/directory
~~~

~~~
$ cat /Path/to/vaults.conf
[Personal]
type=keepass
db_path=/Path/to/Personal.kdbx
password=prompt
keyfile=/Path/to/Personal.key

[Project]
type=keepass
db_path=/Path/to/Project.kdbx
password=Personal:/Head Vaults/Project#field:password
keyfile=/Path/to/Project.key
~~~
___
***Note:***
**Project** will retrieve the keepass password from the **Personal** vault, and **Personal** vault will **prompt** the password on screen to the user
___

~~~
$ cat /Path/to/profiles/directory/project.secrets
[QUA]
VAR@AWS_ACCESS_KEY_ID=Project:/path/to/record1#field:aws_access_keyid
VAR@AWS_SECRET_ACCESS_KEY=Project:/path/to/record2#field:aws_secret_access_key


[Prod]
VAR@AWS_ACCESS_KEY_ID=Project:/path/to/record1#field:aws_access_keyid
VAR@AWS_SECRET_ACCESS_KEY=Project:/path/to/record2#field:aws_secret_access_key
SSH@JUMP_SERVER1:Personal:/path/to/record20#attach:jump_server1.txt
~~~


### DUMP IT!!
And just dump it to get the list of secrets on screen:

~~~
$ secretsintheenv project prod dump table
~~~

or, set the project file path

~~~
$ secretsintheenv /Path/to/profiles/directory/project.secrets prod dump table
~~~

Or, Get the environment variables to be directly used:

**powershell_shell:**
~~~
PS C:\> secretsintheenv.exe C:/Path/to/profiles/directory/project.secrets prod dump powershell_shell
~~~

**cmd_shell:**
~~~
PS C:\> secretsintheenv.exe project prod dump cmd_shell
~~~

**unix_shell:**
~~~
$ secretsintheenv project.secrets prod dump unix_shell
~~~

Or, even, to eval the results to load the variables in the current environment:

~~~
$ eval $(secretsintheenv /Path/to/profiles/directory/project.secrets prod dump unix_shell)
~~~

### RUN IT!!!

Or, if you prefer, just run a command with the loaded secrets in memory (and SSH Key into SSH-Agent)


**On Unix-Like systems:**
~~~
$ secretsintheenv project.secrets prod run /bin/bash
~~~

~~~
$ secretsintheenv /Path/to/profiles/directory/project.secrets prod run /bin/zsh
~~~

**On Windows systems:**
~~~
PS C:\> secretsintheenv.exe C:/Path/to/profiles/directory/project.secrets prod run /bin/zsh
~~~

~~~
C:\> secretsintheenv.exe project prod run /bin/zsh
~~~


## VAULTS

### KeePaas

**Vaults attributes**:
* type=keepass (Mandatory)
* db_path= #Path to .kdbx file (Mandatory)
* password= #if used, the password to unencrypt the db_path file
* keyfile= #if used, the keyfile to unencrypt the db_path file

**Query string format (QUERYSTR)**:

QUERYSTR format is:

~~~
  /path/to/record/into/keepass/file#record_type:record_name
~~~

* **/path/to/record/into/keepass/file** is the path to the record where the secret is stored in the KeePass database
* **record_type**: can get the following values:
  * __field__. To indicate that the secret is stored in a field
  * __attach__. To indicate that the secret is stored as an attachment
* **record_name**: The name of field or attachment where is stored the secret

~~~
Example:
[...]
VAR@AWS_ACCESS_KEY_ID=Project:/path/to/record1#field:aws_access_keyid
[...]
~~~



