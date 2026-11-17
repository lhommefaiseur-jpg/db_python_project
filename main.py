from display import print_table
from vlan_manager import get_vlans, get_vlan, add_vlan, update_vlan, delete_vlan
from subnet_manager import (
    get_subnets,
    get_subnet,
    get_subnets_by_vlan,
    get_subnet_usage,
    add_subnet,
    delete_subnet,
)

def ask_int(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return int(value)
        except ValueError:
            print("Please enter a number.")

# ---------------------------------------------
#    vlan actions
# ----------------------------------------------
def ask_vlan_id(prompt="VLAN ID: "):
    while True:
        vlan_id = ask_int(prompt)
        if 1 <= vlan_id <= 4094:
            return vlan_id
        print("VLAN ID must be between 1 and 4094.")


def list_vlans():
    print_table(get_vlans(), "VLAN LIST")


def create_vlan():
    vlan_id = ask_vlan_id()
    
    if get_vlan(vlan_id) is not None: 
        print(f"VLAN {vlan_id} already exists.")
        return
    name = input("Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    description = input("Description (optional): ").strip() or None

    if add_vlan(vlan_id, name, description):
        print("VLAN added.")


def edit_vlan():
    vlan_id = ask_vlan_id()
    vlan = get_vlan(vlan_id)
    if vlan is None:
        print("That VLAN doesn't exist.")
        return

    print(f"Editing VLAN {vlan_id} (press Enter to keep the current value)")
    name = input(f"Name [{vlan['vlan_name']}]: ").strip() or vlan["vlan_name"]
    description = input(f"Description [{vlan['description']}]: ").strip()
    if not description:
        description = vlan["description"]

    if update_vlan(vlan_id, name, description):
        print("VLAN updated.")


def remove_vlan():
    vlan_id = ask_vlan_id()
    vlan = get_vlan(vlan_id)
    if vlan is None:
        print("That VLAN doesn't exist.")
        return

    confirm = input(f"Delete VLAN {vlan_id} ({vlan['vlan_name']})? [y/N]: ")
    if confirm.strip().lower() != "y":
        print("Cancelled.")
        return

    if delete_vlan(vlan_id):
        print("VLAN deleted.")

# -----------------------------------------------
#       subnet actions
# --------------------------------------------
def list_subnets():
    print_table(get_subnets(), "SUBNET LIST")


def list_subnets_of_vlan():
    vlan_id = ask_vlan_id()
    vlan = get_vlan(vlan_id)
    if vlan is None:
        print("That VLAN doesn't exist.")
        return
    print_table(get_subnets_by_vlan(vlan_id), f"SUBNETS IN VLAN {vlan_id} ({vlan['vlan_name']})")


def show_usage():
    print_table(get_subnet_usage(), "SUBNET USAGE")


def create_subnet():
    vlan_id = ask_vlan_id("VLAN ID for this subnet: ")
    network = input("Network (e.g. 192.168.60.0/24): ").strip()
    gateway = input("Gateway (Enter = first usable address): ").strip() or None

    ok, message = add_subnet(vlan_id, network, gateway)
    print(message)


def remove_subnet():
    subnet_id = ask_int("Subnet ID: ")
    subnet = get_subnet(subnet_id)
    if subnet is None:
        print("That subnet doesn't exist.")
        return

    label = f"{subnet['network_address']}/{subnet['cidr']}"
    confirm = input(f"Delete subnet {label} and all its IP addresses? [y/N]: ")
    if confirm.strip().lower() != "y":
        print("Cancelled.")
        return

    ok, message = delete_subnet(subnet_id)
    print(message)

#-------------------------------------------
#       Menus
#-----------------------------------------------

def vlan_menu():
    while True:
        print("\n--- VLANs ---")
        print("1. List VLANs")
        print("2. Add VLAN")
        print("3. Edit VLAN")
        print("4. Delete VLAN")
        print("0. Back")
        choice = input("Choice: ").strip()

        if choice == "1":
            list_vlans()
        elif choice == "2":
            create_vlan()
        elif choice == "3":
            edit_vlan()
        elif choice == "4":
            remove_vlan()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def subnet_menu():
    while True:
        print("\n--- Subnets ---")
        print("1. List all subnets")
        print("2. List subnets of a VLAN")
        print("3. Subnet usage")
        print("4. Add subnet")
        print("5. Delete subnet")
        print("0. Back")
        choice = input("Choice: ").strip()

        if choice == "1":
            list_subnets()
        elif choice == "2":
            list_subnets_of_vlan()
        elif choice == "3":
            show_usage()
        elif choice == "4":
            create_subnet()
        elif choice == "5":
            remove_subnet()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def main_menu():
    while True:
        print("\n=== IPAM ===")
        print("1. VLANs")
        print("2. Subnets")
        print("0. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            vlan_menu()
        elif choice == "2":
            subnet_menu()
        elif choice == "0":
            print("Bye.")
            break
        else:
            print("Invalid choice.")
if __name__ == "__main__":
    main_menu()
