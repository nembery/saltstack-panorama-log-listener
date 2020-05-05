{% set panorama_user = salt['config.get']('panorama_user') %}
{% set panorama_password = salt['config.get']('panorama_password') %}

get_hostname:
  runner.commit_partial.commit_changes:
   - panorama_ip: {{ data['panorama_ip'] }}
   - panorama_user: {{ panorama_user }}
   - panorama_password: {{ panorama_password }}
   - dg_name: {{ data['dg_name'] }}
   - staging: 'staging'
   - device_serial: "{{ data['device_serial'] | string }}"