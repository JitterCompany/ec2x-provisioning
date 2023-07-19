#!/usr/bin/env python3

import time
import pathlib
import serial
import subprocess
import json
import argparse

from modem import Modem

SERIAL_PORT = pathlib.Path('/dev/ttyUSB3')

FIRMWARE_UPDATE_FOLDER = '/home/odroid/frogwatch/QFirehose_Linux_Android_V1.4.9/'

TARGET_CONFIG = {
    'EC25': {
        'baudrate': '115200',
        'firmware': 'EC25EFAR06A17M4G_20.200.20.200',
        'usb_mode': 'none',
        'apn': 'portalmmm.nl',
        'ecm_mode_roaming': True
    },
    'EC21': {
        'baudrate': '4000000',
        'firmware': 'EC21EFAR06A08M4G_20.200.20.200',
        'usb_mode': 'none',
        'apn': 'portalmmm.nl',
        'ecm_mode_roaming': True
    }
}

def update_firmware(target_version):
    proc = subprocess.run(['make'],
            cwd=FIRMWARE_UPDATE_FOLDER, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not proc.returncode == 0:
        print("ERR: modem update failed (QFirehose failed to build)", proc.stderr.rstrip().decode('utf-8'))
        return False

    proc = subprocess.run(['sudo', './QFirehose', '-f', '../firmware/' + target_version],
            cwd=FIRMWARE_UPDATE_FOLDER, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not proc.returncode == 0:
        print("ERR: modem update failed (QFirehose command failed)", proc.stderr.decode('utf-8'))
        return False

    print("OK: firmware updated!")
    return True

def bootloader_check() -> bool:
    """
    Checks if modem is in bootloader mode by checking for 'Qualcomm' device

    Returns True if modem is verified to be in bootloader
    """
    proc = subprocess.run(['lsusb'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    content = proc.stdout.rstrip().decode("utf-8")

    if 'Quectel' in content:
        return False

    if 'Qualcomm' in content:
        return True

    if not proc.returncode == 0:
        print("lsusb failed: ", proc.stderr.rstrip().decode('utf-8'))
        return False

    return False


def connect(port, baudrate=115200) -> Modem:
    # Configure modem (may take a few iterations)
    iteration = 4
    while iteration:
        iteration-=1

        print("Waiting for modem", end="..")
        serial_port_max_tries = 10
        serial_port_try = 0
        in_bootloader = False
        while not SERIAL_PORT.exists():
            print(end=".")
            time.sleep(2)
            serial_port_try += 1
            if bootloader_check():
                in_bootloader = True
                print("abort")
                print("modem is in bootloader: firmware upgrade required")
                break
            if serial_port_try >= serial_port_max_tries:
                print("timeout..")
                break
        print("")

        if in_bootloader:
            print("Modem in bootloader: Do a manual firmware upgrade with QFirehose:")
            print("> sudo ./QFirehose -f ../firmware/EC2XEFAR06A17M4G_20.200.20.200/")
            return None
            # we don't know what model we're dealing with,

        done = True

        s = None
        serial_tries = 5
        while serial_tries:
            try:
                s = serial.Serial(SERIAL_PORT.as_posix(), timeout=0.5, baudrate=baudrate)
                print("Opened serial port")
                break
            except Exception as e:
                print("Failed to open serial port, trying again in 3 sec")
                serial_tries -= 1
                time.sleep(3)

        if s is None:
            print("Failed to open serial port: powercycle and try again next loop")
            powercycle_modem()
            continue

        modem = Modem(s)
        modem.read_config()
        break

    return modem

def check_update_firmware(modem: Modem, target_config, dry_run=True):
    current_cfg = modem.config

    if target_config['firmware'] and not (current_cfg['firmware'] == target_config['firmware']):
        print(f"Firmware will be updated from {current_cfg['firmware']} to {target_config['firmware']}")
        if not dry_run:
            print("First closing serial port")
            modem.close_serial()

            updated = update_firmware(target_config['firmware'])

            if not updated:
                print("firmware update failed")
    else:
        print("No firmware update needed, already at required version")

def check_update_baudrate(modem: Modem, baudrate, dry_run=True):

    current_cfg = modem.config

    if not current_cfg['baudrate'] == baudrate:
        print(f"Update baudrate to {baudrate}")
        if not dry_run:
            if modem.set_baudrate(baudrate) == True:
                print("Baudrate updated")
            else:
                print("Baudrate update failed")
    else:
        print("Baudrate already correct")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='EC2X Provisioning Tool',
                    description='Verify, update and configure EC21 and EC25 modems',
                    epilog='by Jitter')

    parser.add_argument('--apply', action='store_true', help='Actually apply changes. Without this option this script runs in dry-run mode.')
    parser.add_argument('--baudrate', action='store_true', help='Apply new baudrate')
    parser.add_argument('--update', action='store_true', help='Apply firmware update config and updates')
    parser.add_argument('port', type=pathlib.Path, help="serial port for the AT commands")

    args = parser.parse_args()

    modem = connect(args.port)

    print("Modem config:", modem.config)

    if modem:
        target_config = TARGET_CONFIG[modem.model]

        if args.update:
            print("Updating firmware if required...")
            check_update_firmware(modem, target_config, dry_run=(not args.apply))

        if args.baudrate:
            baudrate = target_config['baudrate']
            check_update_baudrate(modem, baudrate, dry_run=(not args.apply))

            if args.apply:
                modem.close_serial()
                modem = connect(args.port, baudrate)
                if modem.config['baudrate'] == baudrate:
                    print("Baudrate matching requested value")
                else:
                    print(f"Updating baudrate: this will only work if connected to actual uart")
                    print(f"Setting baudrate failed. You can also do this manually with: 'AT+IPR={baudrate};&W' ")

        modem.close_serial()



