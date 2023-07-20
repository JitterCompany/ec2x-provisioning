
import time

class Modem:

    def __init__(self, serial_port):
        self._port = serial_port
        self.model = None
        self.config = None

    def close_serial(self):
        self._port.close()

    def _read_lines(self):
        """Read/flush all available lines from serial"""

        result = []
        while True:
            line = str(self._port.readline(), 'utf-8')
            if not line:
                return result
            result.append(line.strip())

    def _send_bytes(self, data: bytes):
        self._port.write(data)
        return self._read_lines()

    def _send_AT(self, cmd):
        """ Send AT command, returns all resonse lines"""
        self._port.write(bytes(cmd + "\r\n", 'utf-8'))
        return self._read_lines()

    def _validate_connect(self, response):
        if not response[-1] == "CONNECT":
            print("WARN: modem response '{}' not expected".format(response[-1]))
            return False

        return True

    def _validate_response(self, response, expected_n_lines, max_n_lines=-1):
        if not len(response)  == expected_n_lines:
            if (max_n_lines < 0) or (len(response) > max_n_lines):
                print("ERR: modem not responding (expected {} lines, got {})".format
    (expected_n_lines, len(response)))
                return False

        if not response[-1] == "OK":
            print("WARN: modem response '{}' not expected".format(response[-1]))
            return False

        return True

    def set_apn(self, APN):
        at_response = self._send_AT("AT+CGDCONT=1,\"IP\",\"{}\"".format(APN))
        return self._validate_response(at_response, 2)

    def set_usb_mode(self, usb_mode):

        # Modems with AT+QCFG command
        if self.model == 'EC25':
            en_usbnet = '0'
            if usb_mode == 'ecm':
                en_usbnet = '1'
            at_response = self._send_AT("AT+QCFG=\"usbnet\",{}".format(en_usbnet))
            return self._validate_response(at_response, 2)

        # Modems with AT+QCFGEXT command
        elif self.model == 'BG95-M1' or self.model == 'BG95-M3':
            at_response = self._send_AT("AT+QCFGEXT=\"usbnet\",\"{}\"".format(usb_mode))
            return self._validate_response(at_response, 2)

        else:
            print("WARN: set_usb_mode not implemented for model '{}'".format(self.model))
            return False

    def set_baudrate(self, baudrate):

        if self.model == 'EC25' or self.model == 'EC21':
            at_response = self._send_AT(f"AT+IPR={baudrate};&W") # &W for actually writing the settings
            return self._validate_response(at_response, 2)

        print("WARN: set_baudrate not implemented for model '{}'".format(self.model))
        return False

    def get_usb_mode(self):

        # Modems with AT+QCFG command
        if self.model == 'EC25':
            at_response = self._send_AT("AT+QCFG=\"usbnet\"")
            if self._validate_response(at_response, 4):
                at_response = at_response[1].split(',')
                if len(at_response) >= 2 and "usbnet" in at_response[0]:
                    usb_mode = at_response[1].strip('"')
                    if usb_mode == '1':
                        return 'ecm'
                    return 'none'

            print("ERR: could not parse USB mode response")
            return None


        # Modems with AT+QCFGEXT command
        elif self.model == 'BG95-M1' or self.model == 'BG95-M3':

            usb_mode = "unknown"
            at_response = self._send_AT("AT+QCFGEXT=\"usbnet\"")
            if not self._validate_response(at_response, 3):
                # Old firmwares don't support this command yet,
                # so emulate a response stating 'unknown'
                at_response = ['', 'usbnet,unknown', '']

            if len(at_response) >= 2:
                at_response = at_response[1].split(',')
                if not len(at_response) >= 2 or not "usbnet" in at_response[0]:
                    print("ERR: could not parse USB mode response")
                    return None

                usb_mode = at_response[1].strip('"')

            return usb_mode
        else:
            print("WARN: get_usb_mode not implemented for model '{}'".format(self.model))
            return ''



    def set_ecm_mode_roaming(self, enable_ecm_mode_roaming):

        # Modems with AT+QCFG="roamservice" command
        if self.model == 'EC25':
            roam_mode = 1 # disable
            if enable_ecm_mode_roaming:
                roam_mode = 255 # auto
            at_response = self._send_AT("AT+QCFG=\"roamservice\",{},1\r\n".format(roam_mode))
            return self._validate_response(at_response, 2)

        # Modems with qcmap_config file
        elif self.model == 'BG95-M1' or self.model == 'BG95-M3':
            at_response = self._send_AT("AT+QFDEL=\"eufs:/datatx/qcmap_config\"")
            if not self._validate_response(at_response, 2):
                print("WARN: set_ecm_mode_roaming(): could not delete old qcmap_config", at_response[1:])

            ecm_mode_roaming = '1' if enable_ecm_mode_roaming else '0'
            qcmap_data = bytes("Tech=Lte\nProfile=1\nGateway_IP=192.168.225.1\nSubnet=255.255.255.0\nDHCP_Start=192.168.225.20\nDHCP_End=192.168.225.60\nDHCP_Lease=43200\nAutoconnect=1\nRoaming={}".format(ecm_mode_roaming),'utf-8')
            at_response = self._send_AT("AT+QFUPL=\"eufs:/datatx/qcmap_config\",{},5".format(len(qcmap_data)))
            if not at_response[-1] == "CONNECT":
                print("ERR: modem response '{}' not expected".format(at_response[-1]))

                # Wait untill AT+QFUPL command has timed out (otherwise modem may interpret next command as data)
                time.sleep(5+1)
                return False

            self._port.write(qcmap_data)
            at_response = self._read_lines()
            return self._validate_response(at_response, 3)

        else:
            print("ERR: set_ecm_mode_roaming not implemented for model '{}'".format(self.model))
            return False

    def is_roaming_enabled(self):

        # Modems with AT+QCFG="roamservice" command
        if self.model == 'EC25':
            at_response = self._send_AT("AT+QCFG=\"roamservice\"\r\n")
            if self._validate_response(at_response, 4):
                at_response = at_response[1].split(',')
                if len(at_response) >= 2 and "roamservice" in at_response[0]:
                    roam_mode = at_response[1].strip('"')
                    # 255 = auto, 2 = enabled, 1 = off
                    if roam_mode == '255' or roam_mode == '2':
                        return True

            return False

        # Modems with qcmap_config file
        elif self.model == 'BG95-M1' or self.model == 'BG95-M3':
            # Check modem ECM mode roaming setting
            at_response = self._send_AT("AT+QFDWL=\"eufs:/datatx/qcmap_config\"\r\n")
            if not self._validate_response(at_response, 3, max_n_lines=100):
                print("WARN: could not parse ECM roaming response, assuming roaming=0")
                at_response = ['','','roaming=0']


            at_response = [str.strip().lower() for str in at_response]
            ecm_mode_roaming = False
            if len(at_response) >= 3:
                ecm_mode_roaming = "roaming=1" in at_response[2:]
            return ecm_mode_roaming
        else:
            print("WARN: get_ecm_mode_roaming not implemented for model '{}'".format(self.model))
            return False

    def find_file(self, file: str):
        at_response = self._send_AT(f"AT+QFLST=\"{file}\"\r\n")
        print("find file resp: ", at_response)
        if self._validate_response(at_response, 4):
            return at_response
        else:
            print("No files")

    def delete_file(self, filename):
        at_response = self._send_AT(f"AT+QFDEL=\"{filename}\"\r\n")
        if self._validate_response(at_response, 2):
            print("delete OK")

    def upload_file(self, filename, contents: bytes):

        size = len(contents)
        print(f"Uploading {filename} with size {size} and content: {contents}")
        at_response = self._send_AT(f"AT+QFUPL=\"{filename}\",{size}\r\n")

        if self._validate_connect(at_response):
            response = self._send_bytes(contents)
            print("upload bytes response: ", response)
            if self._validate_response(response, 3):
                print("upload OK")
            else:
                print("upload failed")



    def read_config(self):
        try:

            self._read_lines() # Flush

            at_tries = 5
            while at_tries:
                at_response = self._send_AT("AT")
                if self._validate_response(at_response, 2, max_n_lines=20):
                    break
                else:
                    at_tries -= 1
                    print("waiting...")
                    time.sleep(1)

            if at_tries == 0:
                print("Error: modem not responsive")
                return False

            time.sleep(4)

            self._read_lines() # Flush

            ATI = None
            at_response = self._send_AT("ATI")
            model = 'unknown'
            if self._validate_response(at_response, 6):
                _ATI = at_response
                if len(_ATI) == 6:
                    ATI = {
                        'Manufacturer': _ATI[1],
                        'Model': _ATI[2],
                        'Revision': _ATI[3]
                    }
                    print("Modem ID info: ", ATI)
                    self.model = ATI['Model']
                    model = self.model
                    print("Working with model: ", self.model)

            # Check modem firmware version
            at_response = self._send_AT("AT+QGMR")
            if not self._validate_response(at_response, 4):
                return False
            fw_version = ''
            if len(at_response) >= 2:
                fw_version = at_response[1]

            # Check modem APN
            at_response = self._send_AT("AT+CGDCONT?")
            if not self._validate_response(at_response, 4, max_n_lines=6):
                return False

            at_response = at_response[1].split(',')
            if not len(at_response) >= 3:
                print("ERR: could not parse APN response")
                return False
            APN = ''
            if len(at_response) >= 3:
                APN = at_response[2].strip('"')


            # Check baudrate
            at_response = self._send_AT("AT+IPR?")
            if not self._validate_response(at_response, 4):
                return False
            baudrate = ''
            if len(at_response) >= 2:
                baudrate = at_response[1].lstrip("+IPR: ")


            # Check modem USB mode
            usb_mode = self.get_usb_mode()
            if usb_mode is None:
                return False

            ecm_mode_roaming = self.is_roaming_enabled()

            self.config = {
                'model': model,
                'baudrate': baudrate,
                'firmware': fw_version,
                'usb_mode': usb_mode,
                'apn': APN,
                'ecm_mode_roaming': ecm_mode_roaming
            };

            return self.config


        except Exception as e:
            print("Exception: ", e)
        return False
