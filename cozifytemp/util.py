import time

# Homogenize sensor data to contain all fields expected.
# Fill in default values where value isn't available.
def homogenize(sensors):
    out = {}
    for device_id, device in sensors.items():
        if device_id not in out:
            out[device_id] = {}
        out[device_id]['name'] = device['name']

        for field in [
                { 'key': 'temperature', 'default': None, 'type': float },
                { 'key': 'humidity', 'default': None, 'type': float },
                { 'key': 'lastSeen', 'default': int(time.time()*1000), 'type': int }
                ]:
            key = field['key']
            default = field['default']
            type_cast = field['type']
            if key in device['state'] and device['state'][key] is not None:
                # Also make sure values conform to the right types
                out[device_id][key] = type_cast(device['state'][key])
            else:
                out[device_id][key] = default
    return list(out.values())
