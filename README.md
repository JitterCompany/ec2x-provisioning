# EC2X provisioning tool

This requires the following directories to exist:

* `QFirehose_Linux_Android_V1.4.9`
* `firmware/EC21EFAR06A08M4G_20.200.20.200`
* `firmware/EC25EFAR06A17M4G_20.200.20.200`

## Usage

### Check Modem config

```bash
odroid@odroid:~/frogwatch$ ./provision.py /dev/ttyUSB3
Waiting for modem..
Opened serial port
Modem ID info:  {'Manufacturer': 'Quectel', 'Model': 'EC25', 'Revision': 'Revision: EC25EFAR06A17M4G'}
Working with model:  EC25
Modem config: {'model': 'EC25', 'baudrate': '115200', 'firmware': 'EC25EFAR06A17M4G_20.200.20.200', 'usb_mode': 'none', 'apn': 'portalmmm.nl', 'ecm_mode_roaming': True}
```

Run

```bash

./provision.py --help

# for firmware update
./provision.py --update --apply /dev/ttyUSB3

# For baudrate update via usb-serial converter
./provision.py --baudrate --apply /dev/ttySOMEUSBCONVERTER
# e.g. with black magic probe on linux
./provision.py --baudrate --apply /dev/ttyACM1
```

Run without `--apply` to do a dry-run.

Upload key and certificate:

### Provisioning X509 certificates

```bash
# ./provision.py --key ./fwdev1.key --cert ./fwdev1.crt --ca ./sensor_CA.pem /dev/ttyUSB3
./provision.py --key ./proto1_ecdsa.key --cert ./proto1_ecdsa.cert --ca ./frogwatch_ecdsa_CA.pem /dev/ttyUSB3

odroid@odroid:~/frogwatch$ ./provision.py --key ./proto1_ecdsa.key --cert ./proto1_ecdsa.cert --ca ./frogwatch_ecdsa_CA.pem /dev/ttyUSB3
Waiting for modem..
Opened serial port
Modem ID info:  {'Manufacturer': 'Quectel', 'Model': 'EC25', 'Revision': 'Revision: EC25EFAR06A17M4G'}
Working with model:  EC25
Modem config: {'model': 'EC25', 'baudrate': '115200', 'firmware': 'EC25EFAR06A17M4G_20.200.20.200', 'usb_mode': 'none', 'apn': 'portalmmm.nl', 'ecm_mode_roaming': True}
Upload cert proto1_ecdsa.cert
WARN: modem response '+CME ERROR: 418' not expected
Uploading client.crt with size 851 and content: b'-----BEGIN CERTIFICATE-----\nMIICRzCCAeygAwIB<TRIMMED>+9zQ+ymQdKHzFA=\n-----END CERTIFICATE-----\n'
upload bytes response:  ['+QFUPL: 851,6d21', '', 'OK']
upload OK
find file resp:  ['AT+QFLST="client.crt"', '+QFLST: "UFS:client.crt",851', '', 'OK']
Upload key proto1_ecdsa.key
WARN: modem response '+CME ERROR: 418' not expected
Uploading client.key with size 227 and content: b'-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEILl8wIgpeIw4DgjsiuoVEk/Z7owV+PBxWTyFhOtt6vfMoAoGCCqGSM49\nAwEHoUQDQgAEd89NdlcAppNuPSOKTfSTWxPO921PRJb/<TRIMMED>npXlilm1A8VH3Ie2g==\n-----END EC PRIVATE KEY-----\n'
upload bytes response:  ['+QFUPL: 227,d35', '', 'OK']
upload OK
find file resp:  ['AT+QFLST="client.key"', '+QFLST: "UFS:client.key",227', '', 'OK']
Upload ca frogwatch_ecdsa_CA.pem
WARN: modem response '+CME ERROR: 418' not expected
Uploading cacert.pem with size 684 and content: b'-----BEGIN CERTIFICATE-----\nMIIBzDCCAXOgAwIBAgIUDPOISvOAy6/QwPhhNFa183da2+wwCgYIKoZIzj0EAwMw\nOzEbMBkGA1UEAwwSRnJvZ3dhdGNoIEVDRFNBIENBMQ8wDQYDVQQKDAZKaXR0ZXIx\n<TRIMMED>1WfAffKAE=\n-----END CERTIFICATE-----\n'
upload bytes response:  ['+QFUPL: 684,f64', '', 'OK']
upload OK
find file resp:  ['AT+QFLST="cacert.pem"', '+QFLST: "UFS:cacert.pem",684', '', 'OK']
```

### Updating Firmware

```bash
# First a dry run
odroid@odroid:~/frogwatch$ ./provision.py --update /dev/ttyUSB3
Waiting for modem..
Opened serial port
Modem ID info:  {'Manufacturer': 'Quectel', 'Model': 'EC25', 'Revision': 'Revision: EC25EFAR08A04M4G'}
Working with model:  EC25
Modem config: {'model': 'EC25', 'baudrate': '115200', 'firmware': 'EC25EFAR08A04M4G_20.001.20.001', 'usb_mode': 'none', 'apn': 'portalmmm.nl', 'ecm_mode_roaming': True}
Updating firmware if required...
Firmware will be updated from EC25EFAR08A04M4G_20.001.20.001 to EC25EFAR06A17M4G_20.200.20.200
# Add --apply for a real update
odroid@odroid:~/frogwatch$ ./provision.py --update --apply /dev/ttyUSB3
Waiting for modem..
Opened serial port
Modem ID info:  {'Manufacturer': 'Quectel', 'Model': 'EC25', 'Revision': 'Revision: EC25EFAR08A04M4G'}
Working with model:  EC25
Modem config: {'model': 'EC25', 'baudrate': '115200', 'firmware': 'EC25EFAR08A04M4G_20.001.20.001', 'usb_mode': 'none', 'apn': 'portalmmm.nl', 'ecm_mode_roaming': True}
Updating firmware if required...
Firmware will be updated from EC25EFAR08A04M4G_20.001.20.001 to EC25EFAR06A17M4G_20.200.20.200
First closing serial port
OK: firmware updated!
```