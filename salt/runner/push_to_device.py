'''
Palo Alto Networks push_to_device.py
push configuration changes to panorama- device
This software is provided without support, warranty, or guarantee.
Use at your own risk.
'''
import pan.xapi

from .panorama_tools import push_dg
from .panorama_tools import push_stack


def push_to_device(panorama_ip, panorama_user, panorama_password, dg_name, device_serial):
    fw = pan.xapi.PanXapi(api_username=panorama_user, api_password=panorama_password, hostname=panorama_ip)

    # get panorama api key
    api_key = fw.keygen()
    if type(device_serial) is int and len(str(device_serial)) == 14:
        device_serial = '0{0}'.format(device_serial)
        # after commit push the stack and dg update to the fw
    stack = push_stack(fw, dg_name, device_serial)
    device_group = push_dg(fw, dg_name, device_serial)

    # placeholder for any future event.send requirements
    # result = __salt__['event.send']('vistoq/push-to-device',
    #                                {'dg_name': dg_name,
    #                                 'panorama_ip': panorama_ip,
    #                                 'device_serial': device_serial})
    return "A-OK YO %s" % dg_name
