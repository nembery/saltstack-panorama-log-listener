get_hostname:
  runner.push_to_device.push_to_device:
   - panorama_ip: {{ data['panorama_ip'] }}
   - panorama_user: vistoqcontrol
   - panorama_password: Clouds123
   - dg_name: "{{ data['dg_name'] | string }}"
   - device_serial: "{{ data['device_serial'] | string }}"