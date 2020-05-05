get_hostname:
  runner.push_to_device.push_to_device:
   - panorama_ip: {{ data['panorama_ip'] }}
   - panorama_user: some_user
   - panorama_password: some_secret
   - dg_name: "{{ data['dg_name'] | string }}"
   - device_serial: "{{ data['device_serial'] | string }}"