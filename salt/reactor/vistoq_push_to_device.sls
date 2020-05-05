{% set panorama_user = salt['config.get']('panorama_user') %}
{% set panorama_password = salt['config.get']('panorama_password') %}

get_hostname:
  runner.push_to_device.push_to_device:
   - panorama_ip: {{ data['panorama_ip'] }}
   - panorama_user: {{ panorama_user }}
   - panorama_password: {{ panorama_password }}
   - dg_name: "{{ data['dg_name'] | string }}"
   - device_serial: "{{ data['device_serial'] | string }}"