{% set h = data.get('headers', {}) %}
{% set r = h.get('Remote-Addr', '') %}
{% set p = data.get('post', {}) %}
{% set s = p.get('serial', '') %}
{% set d = p.get('description', '') %}
device_connected:
  runner.updates.content_update:
   - panorama_ip: {{ r }}
   - panorama_user: some_user
   - panorama_password: some_secret
   - device_serial: "{{ d.split(":")[1].split(" ")[0] | string }}"
