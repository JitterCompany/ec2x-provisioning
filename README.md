# EC2X provisioning tool

This requires the following directories to exist:

* `QFirehose_Linux_Android_V1.4.9`
* `firmware/EC21EFAR06A08M4G_20.200.20.200`
* `firmware/EC25EFAR06A17M4G_20.200.20.200`

## Usage

Run

```bash

./provision.py --help

# for firmware update
./provision.py --update --apply /dev/ttyUSB3

# For baudrate update via usb-serial converter
./provision.py --baudrate --apply /dev/ttySOMEUSBCONVERTER
```

Run without `--apply` to do a dry-run.

Upload key and certificate:

```bash
./provision.py --key ./fwdev1.key --cert ./fwdev1.crt --ca ./sensor_CA.pem /dev/ttyUSB3
```
