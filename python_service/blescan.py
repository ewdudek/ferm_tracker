# based on https://github.com/atlefren/pytilt/blob/master/blescan.py

# TODO
# Trim down by removing unused code
# Investigate performance
# Allow for multiple tilts

import os
import sys
import struct
import bluetooth._bluetooth as bluez

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS = 0x00
LE_RANDOM_ADDRESS = 0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE = 7
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C
OCF_LE_CREATE_CONN = 0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02
EVT_LE_CONN_UPDATE_COMPLETE = 0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE = 0x04

# Advertisment event types
ADV_IND = 0x00
ADV_DIRECT_IND = 0x01
ADV_SCAN_IND = 0x02
ADV_NONCONN_IND = 0x03
ADV_SCAN_RSP = 0x04

# Only look for the purple uuid
TILTS = {
		'a495bb40c5b14b44b5121370f02d74de': 'Purple',
        #'a495bb10c5b14b44b5121370f02d74de': 'Red',
        #'a495bb20c5b14b44b5121370f02d74de': 'Green',
        #'a495bb30c5b14b44b5121370f02d74de': 'Black',
        #'a495bb50c5b14b44b5121370f02d74de': 'Orange',
        #'a495bb60c5b14b44b5121370f02d74de': 'Blue',
        #'a495bb70c5b14b44b5121370f02d74de': 'Yellow',
        #'a495bb80c5b14b44b5121370f02d74de': 'Pink',
}

def returnnumberpacket(pkt):
    integer = 0
    multiple = 256
    for i in pkt:
        integer += i * multiple
        multiple = 1
    return integer
    
#just turn it into a hex string
def returnstringpacket(pkt):
    ret = ""
    for c in pkt:
        ret += "%x" % c
    return ret

def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)

def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

def hci_le_set_scan_parameters(sock):
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    SCAN_RANDOM = 0x01
    OWN_TYPE = SCAN_RANDOM
    SCAN_TYPE = 0x01

def parse_events(sock, loop_count=100):
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
    beacons = []
    for i in range(0, loop_count):
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack('BBB', pkt[:3])
        if event == LE_META_EVENT:
            subevent = pkt[3]
            pkt = pkt[4:]
            if subevent == EVT_LE_CONN_COMPLETE:
                le_handle_connection_complete(pkt)
            elif subevent == EVT_LE_ADVERTISING_REPORT:
                num_reports = pkt[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                    uuid = returnstringpacket(pkt[report_pkt_offset - 22: report_pkt_offset - 6])
                    #if one of the beacons matches known tilt keys (only purple matters)
                    if uuid in TILTS.keys():
                        beacons.append({
                            'color': TILTS.get(uuid),
                            'grav': returnnumberpacket(pkt[report_pkt_offset - 4: report_pkt_offset - 2])/1000,
                            'temp': returnnumberpacket(pkt[report_pkt_offset - 6: report_pkt_offset - 4])
                        })
                        #I only have 1 tilt for now, so just break and return the valid datapoint
                        break
                done = True #WHAT IS THIS????
        # Quit scanning after the first hit
        if len(beacons) > 0 :
            break
            
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, old_filter)
    return beacons
