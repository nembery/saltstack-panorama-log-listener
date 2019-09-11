# Saltstack Event / Log Listener

This is a simple example of how to set up a log listener to execute arbitrary python code in response to various logs


## Basic flow

1. Set up HTTP log forwarding profile in PAN-OS, the URI to send the logs will be something 
like /vistoq/device-connected

2. Configure a entry in the 'reactor.conf' such as:
    ```bash
        # the event URI /vistoq/device-connected will map to the vistoq_device_connected.sls file
      - 'salt/netapi/hook/vistoq/device-connected':
        - /srv/salt/reactor/vistoq_device_connected.sls
    ```

3. Create the reactor sls file to map the event structure to your python code

    ```bash
    # this sls file recieves two objects: data and tag
    # the data object is a dict created from the JSON payload that is recieved on the webhook
    # the whole point of this file is to map the recieved json payload to the function arguments
    # required for our code
    # this SLS file is jinja interpolated, so normal jinja syntax applies
    # set a variable named H that contains the contents of the 'headers' attributes in the payload
    {% set h = data.get('headers', {}) %}
    # get the remote-address from the headers and set as r
    {% set r = h.get('Remote-Addr', '') %}
    # get the post attribute from the data
    {% set p = data.get('post', {}) %}
    # get the serial number from the posted payload
    {% set s = p.get('serial', '') %}
    # and get the description
    {% set d = p.get('description', '') %}
    
    # top level is just an arbitrary name 
    content_update:
      # to keep things simple, we are using a runner, which is a bit of python code found in 
      # salt/runner directory. This will execute the content_update function in the 'updates.py'
      # The will send in the 4 keyword arguments listed below
      runner.updates.content_update:
       - panorama_ip: {{ r }}
       - panorama_user: vistoqcontrol
       - panorama_password: Clouds123
       - device_serial: "{{ d.split(":")[1].split(" ")[0] | string }}" 
   ```
 
 4. Create your python code in the salt/runner directory
 
    ```python
    # create a function that matches that listed in your reactor file above
    def content_update(panorama_ip, panorama_user, panorama_password, device_serial)
    ```
   
5. Use docker-compose to bring up the saltstack container and map in the config files as necessary 