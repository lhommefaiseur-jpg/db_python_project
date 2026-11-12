from database import run_query, run_command


def get_vlans():
    return run_query(
        "SELECT vlan_id, vlan_name, description FROM vlans ORDER BY vlan_id"
    )


def get_vlan(vlan_id):
    rows = run_query(
        "SELECT vlan_id, vlan_name, description FROM vlans WHERE vlan_id = %s",
        (vlan_id,),
    )
    return rows[0] if rows else None


def add_vlan(vlan_id, name, description=None):
    return run_command(
        "INSERT INTO vlans (vlan_id, vlan_name, description) VALUES (%s, %s, %s)",
        (vlan_id, name, description),
    )


def update_vlan(vlan_id, name, description=None):
    return run_command(
        "UPDATE vlans SET vlan_name = %s, description = %s WHERE vlan_id = %s",
        (name, description, vlan_id),
    )


def delete_vlan(vlan_id):
    return run_command("DELETE FROM vlans WHERE vlan_id = %s", (vlan_id,))
