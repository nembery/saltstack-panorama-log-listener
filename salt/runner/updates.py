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

import pan.xapi

from .panorama_tools import get_latest_content
from .panorama_tools import update_content


def content_update(panorama_ip, panorama_user, panorama_password, device_serial):
    fw = pan.xapi.PanXapi(api_username=panorama_user, api_password=panorama_password, hostname=panorama_ip)
    # get panorama api key
    api_key = fw.keygen()
    print(device_serial)
    if type(device_serial) is int and len(str(device_serial)) == 14:
        device_serial = '0{0}'.format(device_serial)
    print('updating content for NGFW serial number {0}'.format(device_serial))
    # !!! updates require panorama mgmt interface with internet access
    # update ngfw to latest content and av versions
    # passing in the serial number for device to update
    for item in ['content', 'anti-virus']:
        filename = get_latest_content(fw, item)
        update_content(fw, item, device_serial, filename)

    result = __salt__['event.send']('vistoq/move-device', {'device_serial': device_serial, 'panorama_ip': panorama_ip})

    return "A-OK YO %s" % device_serial


if __name__ == '__main__':
    main()
