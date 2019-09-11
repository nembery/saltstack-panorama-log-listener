get_hostname:
  runner.move_device.move_device:
   - panorama_ip: {{ data['panorama_ip'] }}
   - panorama_user: vistoqcontrol
   - panorama_password: Clouds123
   - device_serial: "{{ data['device_serial'] | string }}"
   - dg_name: 'staging'