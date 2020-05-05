get_hostname:
  runner.commit_partial.commit_changes:
   - panorama_ip: {{ data['panorama_ip'] }}
   - panorama_user: some_user
   - panorama_password: some_secret
   - dg_name: {{ data['dg_name'] }}
   - staging: 'staging'
   - device_serial: "{{ data['device_serial'] | string }}"