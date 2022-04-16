# Ansible inventory file to ssh config
This is a python tool for updating ssh config from ansible inventory file.


## Install

``` bash
$ pip3 install --user AISTool
```

From github:

``` bash
$ pip3 install --user git+https://github.com/rasjani/AISTool
```

Local install

``` bash
$ git clone https://github.com/rasjani/AISTool.git
$ pip3 install .
```

## Usage

``` bash
$ AISTool -h
usage: AISTool [-h] [-o OUTPUT] [-d] [--with-backup] inventory_file

positional arguments:
  inventory_file        ansible inventory file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        ssh config output path (default: ~/.ssh/config)
  -d, --dry-run         show new configurations without updating file
  --without-backup      update without backup

# Update ~/.ssh/config from specified inventory file
$ AISTool $INVENTORY_FILE

# Update without backup
$ AISTool $INVENTORY_FILE --without-backup

# Output as a new file
$ AISTool $INVENTORY_FILE -o new_ssh_config

# Show content without output
$ AISTool $INVENTORY_FILE -d
```

## Example

``` bash
# Input (Inventory File)
$ cat hosts

[group_1]
node1 ansible_ssh_host=192.168.0.5
node2 ansible_ssh_host=192.168.0.6

[group_2]
node3 ansible_host=192.168.0.7
node4 ansible_host=192.168.0.8

# Commnad
$ AISTool hosts -o newconfig
Inventory: hosts
Target: newconfig
No such file, generate a new file: new_ssh_config ...

# Output (SSH Config Format)
$ cat new_ssh_config

Host node1
  HostName 192.168.0.5


Host node2
  HostName 192.168.0.6


Host node3
  HostName 192.168.0.7


Host node4
  HostName 192.168.0.8
```
