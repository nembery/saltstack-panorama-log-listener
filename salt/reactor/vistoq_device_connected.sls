{% set h = data.get('headers', {}) %}
{% set r = h.get('Remote-Addr', '') %}
{% set p = data.get('post', {}) %}
{% set s = p.get('serial', '') %}
{% set d = p.get('description', '') %}

{% set panorama_user = salt['config.get']('panorama_user') %}
{% set panorama_password = salt['config.get']('panorama_password') %}

{% if d != '' %}

device_connected:
  runner.updates.content_update:
   - panorama_ip: {{ r }}
   - panorama_user: {{ panorama_user }}
   - panorama_password: {{ panorama_password }}
   - device_serial: '{{ d.split(":")[1].split(" ")[0] | string }}'

{% endif %}