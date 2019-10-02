# hacc-floureon-tuya
Home Assistant Custom Component for Floureon thermostat HY08WE

This is like this one:
https://images-na.ssl-images-amazon.com/images/I/51Hu0eGiJ5L._SL1024_.jpg

```
climate:
  - platform: localtuya
    host: 192.168.x.x (your thermostat IP)
    local_key: thermostat local_key
    device_id: thermostat local_id
    name: thermostat name
    scan_interval: 5
    min_temp: 5
    max_temp: 35
    protocol_version: 3.3
```
