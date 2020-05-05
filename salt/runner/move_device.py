# Copyright (c) 2018, Palo Alto Networks
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Author: Scott Shoaf <sshoaf@paloaltonetworks.com>

'''
Palo Alto Networks move_device.py

uses panorama install content updates to a managed firewall
does both content/threat and antivirus updates

This software is provided without support, warranty, or guarantee.
Use at your own risk.
'''
import pan.xapi

from panorama_tools import get_hostname
from panorama_tools import move_dg
from panorama_tools import move_ts


def move_device(panorama_ip, panorama_user, panorama_password, device_serial, dg_name):
    fw = pan.xapi.PanXapi(api_username=panorama_user, api_password=panorama_password, hostname=panorama_ip)

    # get panorama api key
    api_key = fw.keygen()
    if type(device_serial) is int and len(str(device_serial)) == 14:
        device_serial = '0{0}'.format(device_serial)
        # hostname for input serial number
    hostname = get_hostname(fw, device_serial, dg_name)
    print('hostname is', hostname)
    # take hostname and staging inputs to set source and dest device-groups and stacks
    from_dg, to_dg = dg_name, hostname
    from_ts, to_ts = dg_name, hostname

    print('moving NGFW serial number {0} to device-group {1}'.format(device_serial, to_dg))
    move_dg(fw, device_serial, from_dg, to_dg)
    print('moving NGFW serial number {0} to template_stack {1}'.format(device_serial, to_ts))
    move_ts(fw, device_serial, from_ts, to_ts)
    # sending hostname as the dg_name as the dg and stack to commit
    # original dg_name in is the staging dg name
    result = __salt__['event.send']('vistoq/commit-partial',
                                    {'dg_name': hostname,
                                     'panorama_ip': panorama_ip,
                                     'device_serial': device_serial})
    return "A-OK YO %s" % hostname
