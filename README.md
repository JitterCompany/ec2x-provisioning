# EC2X provisioning tool

This requires the following directories to exist:

* `QFirehose_Linux_Android_V1.4.9`
* `firmware/EC21EFAR06A08M4G_20.200.20.200`
* `firmware/EC25EFAR06A17M4G_20.200.20.200`

## Usage

Run

```
./provision --help

# for firmware update
./provision --update --apply /dev/ttyUSB3

# For baudrate update via usb-serial converter
./provision --baudrate --apply /dev/ttySOMEUSBCONVERTER
```

Run without `--apply` to do a dry-run.
