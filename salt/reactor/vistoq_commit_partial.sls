get_hostname:
  runner.commit_partial.commit_changes:
   - panorama_ip: {{ data['panorama_ip'] }}
   - panorama_user: vistoqcontrol
   - panorama_password: Clouds123
   - dg_name: {{ data['dg_name'] }}
   - staging: 'staging'
   - device_serial: "{{ data['device_serial'] | string }}"