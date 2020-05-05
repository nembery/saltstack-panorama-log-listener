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
Palo Alto Networks commit_partial.py

do a partial commit to named  device-group and template-stack

This software is provided without support, warranty, or guarantee.
Use at your own risk.
'''
import pan.xapi

from panorama_tools import commit_partial


def commit_changes(panorama_ip, panorama_user, panorama_password, dg_name, staging, device_serial):
    fw = pan.xapi.PanXapi(api_username=panorama_user, api_password=panorama_password, hostname=panorama_ip)

    # get panorama api key
    api_key = fw.keygen()
    print('commit partial for {0}'.format(dg_name))
    dg_commit = commit_partial(fw, staging, dg_name, panorama_user)
    result = __salt__['event.send']('vistoq/push-to-device',
                                    {'dg_name': dg_name,
                                     'panorama_ip': panorama_ip,
                                     'device_serial': device_serial})
    return "A-OK YO %s" % dg_name
