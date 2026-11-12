
CREATE DATABASE ipam_db;
USE ipam_db;

-- =================================
-- 1. VLAN TABLE
-- =================================

CREATE TABLE vlans (
    vlan_id INT PRIMARY KEY,
    vlan_name VARCHAR(50) NOT NULL,
    description VARCHAR(255)
);

-- =================================
-- 2. SUBNET TABLE
-- =================================

CREATE TABLE subnets (
    subnet_id INT AUTO_INCREMENT PRIMARY KEY,
    vlan_id INT NOT NULL, 
    network_address VARCHAR(15) NOT NULL,
    cidr TINYINT NOT NULL,
    gateway VARCHAR(15),
    FOREIGN KEY (vlan_id)
        REFERENCES vlans(vlan_id),
    CHECK (cidr BETWEEN 0 AND 32),
    UNIQUE (network_address, cidr)
);

-- =================================
-- 3. IP ADDRESSES TABLE
-- =================================

CREATE TABLE ip_addresses (
    ip_id INT AUTO_INCREMENT PRIMARY KEY,
    subnet_id INT NOT NULL,
    ip_address VARCHAR(15) NOT NULL,
    status ENUM('available', 'allocated', 'reserved')
        DEFAULT 'available',
    FOREIGN KEY (subnet_id)
        REFERENCES subnets(subnet_id),

    UNIQUE (subnet_id, ip_address)
);

-- =================================
-- 4. DEVICES TABLE
-- =================================

CREATE TABLE devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    ip_id INT NOT NULL UNIQUE,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50),

    FOREIGN KEY (ip_id)
        REFERENCES ip_addresses(ip_id)
);






-- 1. VLANs
INSERT INTO vlans (vlan_id, vlan_name, description) VALUES
(10, 'Sales',      'Sales department workstations'),
(20, 'IT',         'IT staff and admin machines'),
(30, 'HR',         'Human resources'),
(40, 'Servers',    'Internal servers'),
(50, 'Guest',      'Guest Wi-Fi, isolated from internal network'),
(99, 'Management', 'Network device management');

-- 2. Subnets (subnet_id 1 to 6, assigned automatically in this order)
INSERT INTO subnets (vlan_id, network_address, cidr, gateway) VALUES
(10, '192.168.10.0', 24, '192.168.10.1'),
(20, '192.168.20.0', 24, '192.168.20.1'),
(30, '192.168.30.0', 24, '192.168.30.1'),
(40, '10.0.40.0',    24, '10.0.40.1'),
(50, '172.16.50.0',  24, '172.16.50.1'),
(99, '10.0.99.0',    28, '10.0.99.1');

-- 3. IP addresses (the subnet_id values assume the tables were empty before)
INSERT INTO ip_addresses (subnet_id, ip_address, status) VALUES
-- VLAN 10
(1, '192.168.10.1',  'reserved'),
(1, '192.168.10.10', 'allocated'),
(1, '192.168.10.11', 'allocated'),
(1, '192.168.10.50', 'available'),
(1, '192.168.10.51', 'available'),
-- VLAN 20
(2, '192.168.20.1',   'reserved'),
(2, '192.168.20.10',  'allocated'),
(2, '192.168.20.11',  'allocated'),
(2, '192.168.20.12',  'allocated'),
(2, '192.168.20.100', 'available'),
-- VLAN 30
(3, '192.168.30.1',  'reserved'),
(3, '192.168.30.10', 'allocated'),
(3, '192.168.30.20', 'available'),
-- VLAN 40
(4, '10.0.40.1',  'reserved'),
(4, '10.0.40.10', 'allocated'),
(4, '10.0.40.11', 'allocated'),
(4, '10.0.40.12', 'available'),
-- VLAN 50
(5, '172.16.50.1',   'reserved'),
(5, '172.16.50.100', 'available'),
(5, '172.16.50.101', 'available'),
-- VLAN 99
(6, '10.0.99.1', 'reserved'),
(6, '10.0.99.2', 'allocated'),
(6, '10.0.99.3', 'allocated');

-- 4. Devices (only on allocated IPs; ip_id is looked up by address)
INSERT INTO devices (ip_id, device_name, device_type)
SELECT ip_id, 'PC-SALES-01', 'workstation' FROM ip_addresses WHERE ip_address = '192.168.10.10'
UNION ALL
SELECT ip_id, 'PC-SALES-02', 'workstation' FROM ip_addresses WHERE ip_address = '192.168.10.11'
UNION ALL
SELECT ip_id, 'PC-IT-01',    'workstation' FROM ip_addresses WHERE ip_address = '192.168.20.10'
UNION ALL
SELECT ip_id, 'PC-IT-02',    'laptop'      FROM ip_addresses WHERE ip_address = '192.168.20.11'
UNION ALL
SELECT ip_id, 'PRINTER-IT',  'printer'     FROM ip_addresses WHERE ip_address = '192.168.20.12'
UNION ALL
SELECT ip_id, 'PC-HR-01',    'workstation' FROM ip_addresses WHERE ip_address = '192.168.30.10'
UNION ALL
SELECT ip_id, 'SRV-DNS',     'server'      FROM ip_addresses WHERE ip_address = '10.0.40.10'
UNION ALL
SELECT ip_id, 'SRV-FILES',   'server'      FROM ip_addresses WHERE ip_address = '10.0.40.11'
UNION ALL
SELECT ip_id, 'SW-CORE-01',  'switch'      FROM ip_addresses WHERE ip_address = '10.0.99.2'
UNION ALL
SELECT ip_id, 'SW-ACCESS-01','switch'      FROM ip_addresses WHERE ip_address = '10.0.99.3';
