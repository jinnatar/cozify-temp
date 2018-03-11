import time

# Homogenize sensor data to contain all fields expected.
# Fill in default values where value isn't available.
def homogenize(sensors):
    out = {}
    for device_id, device in sensors.items():
        if device_id not in out:
            out[device_id] = {}
        out[device_id]['name'] = device['name']

        for key, default in {
                'temperature': None,
                'humidity': None,
                'lastSeen': int(time.time()*1000)
                }.items():
            if key in device['state']:
                # Also make sure values are floats so field type is maintained
                out[device_id][key] = float(device['state'][key])
            else:
                out[device_id][key] = default
    return list(out.values())
