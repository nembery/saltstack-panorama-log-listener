{% set panorama_user = salt['config.get']('panorama_user') %}
{% set panorama_password = salt['config.get']('panorama_password') %}

get_hostname:
  runner.move_device.move_device:
   - panorama_ip: {{ data['panorama_ip'] }}
   - panorama_user: {{ panorama_user }}
   - panorama_password: {{ panorama_password }}
   - device_serial: "{{ data['device_serial'] | string }}"
   - dg_name: 'staging'