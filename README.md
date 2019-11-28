# hacc-floureon-tuya
Home Assistant Custom Component for Floureon thermostat HY08WE

This is like this one:
https://images-na.ssl-images-amazon.com/images/I/51Hu0eGiJ5L._SL1024_.jpg

Put this configuration in your HA configuration.yaml file.
Values are the same as the official Tuya integration:
https://www.home-assistant.io/integrations/tuya/

```
floureon:
  username: <YOUR_TUYA_USERNAME> 
  password: <YOUR_TUYA_PASSWORD>
  country_code: <YOUR_ACCOUNT_COUNTRYCODE>
  platform: <tuya|smart_life|jinvoo_smart>
 ```
