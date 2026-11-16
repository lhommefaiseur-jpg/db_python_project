import ipaddress

from mysql.connector import Error

from database import connection_db, run_query, run_transaction
from vlan_manager import get_vlan

MIN_CIDR = 22
MAX_CIDR = 30


def get_subnets():
    return run_query(
        """
        SELECT s.subnet_id,
               CONCAT(s.network_address, '/', s.cidr) AS network,
               s.gateway,
               s.vlan_id,
               v.vlan_name
        FROM subnets s
        JOIN vlans v ON v.vlan_id = s.vlan_id
        ORDER BY s.subnet_id
        """
    )


def get_subnet(subnet_id):
    rows = run_query(
        """
        SELECT subnet_id, vlan_id, network_address, cidr, gateway
        FROM subnets
        WHERE subnet_id = %s
        """,
        (subnet_id,),
    )
    return rows[0] if rows else None


def get_subnets_by_vlan(vlan_id):
    return run_query(
        """
        SELECT s.subnet_id,
               CONCAT(s.network_address, '/', s.cidr) AS network,
               s.gateway
        FROM subnets s
        WHERE s.vlan_id = %s
        ORDER BY s.subnet_id
        """,
        (vlan_id,),
    )


def get_subnet_usage():
    """How many IPs are allocated / reserved / available in each subnet."""
    return run_query(
        """
        SELECT s.subnet_id,
               CONCAT(s.network_address, '/', s.cidr) AS network,
               v.vlan_name,
               COUNT(i.ip_id) AS total,
               COUNT(CASE WHEN i.status = 'allocated' THEN 1 END) AS allocated,
               COUNT(CASE WHEN i.status = 'reserved'  THEN 1 END) AS reserved,
               COUNT(CASE WHEN i.status = 'available' THEN 1 END) AS available
        FROM subnets s
        JOIN vlans v ON v.vlan_id = s.vlan_id
        LEFT JOIN ip_addresses i ON i.subnet_id = s.subnet_id
        GROUP BY s.subnet_id, s.network_address, s.cidr, v.vlan_name
        ORDER BY s.subnet_id
        """
    )


def add_subnet(vlan_id, network_text, gateway=None):
    if get_vlan(vlan_id) is None:
        return False, f"VLAN {vlan_id} doesn't exist. Create it first."

    try:
        network = ipaddress.ip_network(network_text, strict=True)
    except ValueError:
        return False, (
            "Invalid network address or CIDR prefix."
            "(the address must be the network address, not a host)."
        )

    if network.version != 4:
        return False, "Only IPv4 is supported."

    if not MIN_CIDR <= network.prefixlen <= MAX_CIDR:
        return False, f"Prefix must be between /{MIN_CIDR} and /{MAX_CIDR}."

    for row in run_query("SELECT network_address, cidr FROM subnets"):
        existing = ipaddress.ip_network(
            f"{row['network_address']}/{row['cidr']}", strict=False
        )
        if network.overlaps(existing):
            return False, f"Overlaps with existing subnet {existing}."

    hosts = list(network.hosts())
    if gateway is None:
        gateway_ip = hosts[0]
    else:
        try:
            gateway_ip = ipaddress.ip_address(gateway)
        except ValueError:
            return False, "Invalid gateway address."
        if gateway_ip not in hosts:
            return False, f"Gateway {gateway_ip} is not a usable address in {network}."

    connection = connection_db()
    if connection is None:
        return False, "Could not connect to the database."

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO subnets (vlan_id, network_address, cidr, gateway) "
            "VALUES (%s, %s, %s, %s)",
            (vlan_id, str(network.network_address), network.prefixlen, str(gateway_ip)),
        )
        subnet_id = cursor.lastrowid

        ip_rows = [
            (subnet_id, str(ip), "reserved" if ip == gateway_ip else "available")
            for ip in hosts
        ]
        cursor.executemany(
            "INSERT INTO ip_addresses (subnet_id, ip_address, status) "
            "VALUES (%s, %s, %s)",
            ip_rows,
        )
        connection.commit()
        return True, f"Subnet {network} added with {len(ip_rows)} IP addresses."
    except Error as e:
        connection.rollback()
        return False, f"Database error: {e}"
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def delete_subnet(subnet_id):
    if get_subnet(subnet_id) is None:
        return False, "That subnet doesn't exist."

    result = run_query(
        """
        SELECT COUNT(*) AS n
        FROM devices d
        JOIN ip_addresses i ON i.ip_id = d.ip_id
        WHERE i.subnet_id = %s
        """,
        (subnet_id,),
    )
    if not result:
        return False, "Could not check the devices in this subnet."
    if result[0]["n"] > 0:
        return False, f"Subnet still has {result[0]['n']} device(s). Remove them first."

    ok = run_transaction(
        [
            ("DELETE FROM ip_addresses WHERE subnet_id = %s", (subnet_id,)),
            ("DELETE FROM subnets WHERE subnet_id = %s", (subnet_id,)),
        ]
    )
    if ok:
        return True, "Subnet deleted."
    return False, "Could not delete the subnet."
