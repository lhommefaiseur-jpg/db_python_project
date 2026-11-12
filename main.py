from display import print_table
from vlan_manager import get_vlans, get_vlan, add_vlan, update_vlan, delete_vlan


def ask_int(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return int(value)
        except ValueError:
            print("Please enter a number.")


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


def menu():
    while True:
        print("\n=== IPAM ===")
        print("1. List VLANs")
        print("2. Add VLAN")
        print("3. Edit VLAN")
        print("4. Delete VLAN")
        print("0. Exit")
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
            print("Bye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    menu()
