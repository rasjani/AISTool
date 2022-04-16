from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from sshconf import read_ssh_config, empty_ssh_config_file
from pathlib import Path
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from pkg_resources import get_distribution
from shutil import copyfile
from datetime import datetime


BACKUP_EXTENSION_FORMAT = "%Y%m%d_%H%M%S"


def get_args():
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-v", "--version", action="version", version=get_distribution("AISTool").version
    )
    parser.add_argument("inventory_file", help="ansible inventory file")
    parser.add_argument(
        "-o", "--output", help="ssh config output path (default: ~/.ssh/config)", default="~/.ssh/config", type=Path
    )
    parser.add_argument("-g", "--group", help="ansible inventory group to use", default="all")
    parser.add_argument("-u", "--user", help="overwrite ansible_user", default=None)
    parser.add_argument("-i", "--identityfile", help="Add external identity file", default=None, type=Path)
    parser.add_argument("-d", "--dry-run", help="show new configurations without updating file", action="store_true")
    parser.add_argument("--without-backup", help="update without backup", action="store_true", default=False)

    return parser.parse_args()


def update_ssh_config(ssh_config, inventories, variables, group="all", user=None, identity=None):
    def _get_key(vars, keynames):
        value = vars.get(keynames[0], vars.get(keynames[1], None))
        if not value:
            raise KeyError(f"Provided dictionary does not contain values for given keys: {keynames}")
        return value

    for host in inventories.get_hosts(group):
        host_var = variables.get_vars(host=host)
        host_name = host.get_name()
        ssh_config_options = {}

        try:
            ssh_config_options["HostName"] = _get_key(host_var, ("ansible_host", "ansible_ssh_host"))
        except KeyError:
            print("Failed to get [{}] ssh address... ".format(host))
            continue

        try:
            ssh_config_options["Port"] = _get_key(host_var, ("ansible_port", "ansible_ssh_port"))
        except KeyError:
            # Field is not mandatory, no need to do error handling
            pass

        try:
            if user:
                ssh_config_options["User"] = user
            else:
                ssh_config_options["User"] = _get_key(host_var, ("ansible_user", "ansible_ssh_user"))
        except KeyError:
            # Field is not mandatory, no need to do error handling
            pass

        try:
            if identity and identity.exists():
                ssh_config_options["IdentityFile"] = identity
            else:
                ssh_config_options["IdentityFile"] = _get_key(host_var, ("ansible_private_key_file", "ansible_ssh_private_key_file"))
        except KeyError:
            # Field is not mandatory, no need to do error handling
            pass

        try:
            ssh_config.set(host_name, **ssh_config_options)
        except ValueError:
            ssh_config.add(host_name, **ssh_config_options)


def backup(target_file):
    destination = f"{target_file}.{datetime.now().strftime(BACKUP_EXTENSION_FORMAT)}"
    copyfile(target_file, destination)


def print_ssh_config(ssh_config):
    for h in ssh_config.hosts():
        print(h, ssh_config.host(h))


def ansible_inventory_to_ssh_config(inventory_file, output, dry_run=False, with_backup=True, group="all", user=None, identity=None):
    print(f"Inventory: {inventory_file}")
    print(f"Target: {output}")

    loader = DataLoader()
    inventories = InventoryManager(loader=loader, sources=[inventory_file])
    variables = VariableManager(loader=loader, inventory=inventories)

    try:
        ssh_config = read_ssh_config(output)
        update_ssh_config(ssh_config, inventories, variables, group, user, identity)

        if with_backup:
            backup(output)

        if dry_run:
            print_ssh_config(ssh_config)
        else:
            ssh_config.save()
    except FileNotFoundError:
        ssh_config = empty_ssh_config_file()
        update_ssh_config(ssh_config, inventories, variables, group, user, identity)

        if dry_run:
            print_ssh_config(ssh_config)
        else:
            print(f"No such file, generate a new file: {output} ...")
            ssh_config.write(output)


def main():
    args = get_args()
    ansible_inventory_to_ssh_config(
        args.inventory_file, args.output.expanduser(), args.dry_run, not args.without_backup, args.group, args.user, args.identityfile
    )
