get_hostname:
  runner.move_device.move_device:
   - panorama_ip: {{ data['panorama_ip'] }}
   - panorama_user: some_user
   - panorama_password: some_secret
   - device_serial: "{{ data['device_serial'] | string }}"
   - dg_name: 'staging'