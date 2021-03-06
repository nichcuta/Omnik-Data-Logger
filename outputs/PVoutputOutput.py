import PluginLoader
import datetime
import urllib
import urllib2


class PVoutputOutput(PluginLoader.Plugin):
    """Sends the data from the Omnik inverter to PVoutput.org"""

    def process_message(self, msg):
        """Send the information from the inverter to PVoutput.org.

        Args:
            msg (InverterMsg.InverterMsg): Message to process

        """
        now = datetime.datetime.now()
        serial = self.config.get('inverter', 'serial')

        if (now.minute % 5) == 0:  # Only run at every 5 minute interval

            if msg.status == 'NO INVERTER DATA':
                self.logger.error('Inverter Status Fault. Message:')
                msg.dump()

            elif msg.aknowledge == 'DATA SEND IS OK':
                self.logger.debug('Aknowledgement message received: DATA SEND IS OK')
 
            elif msg.id == serial:

                self.logger.info('Uploading to PVoutput')

                url = "http://pvoutput.org/service/r2/addstatus.jsp"

                if self.config.getboolean('inverter', 'use_temperature'):
                    get_data = {
                        'key': self.config.get('pvout', 'apikey'),
                        'sid': self.config.get('pvout', 'sysid'),
                        'd': now.strftime('%Y%m%d'),
                        't': now.strftime('%H:%M'),
                        'v1': msg.e_today * 1000,
                        'v2': msg.p_ac(1),
                        'v5': msg.temperature,
                        'v6': msg.v_ac(1)
                    }
                else:
                    get_data = {
                        'key': self.config.get('pvout', 'apikey'),
                        'sid': self.config.get('pvout', 'sysid'),
                        'd': now.strftime('%Y%m%d'),
                        't': now.strftime('%H:%M'),
                        'v1': msg.e_today * 1000,
                        'v2': msg.p_ac(1),
                        'v6': msg.v_pv(1)
                    }

                get_data_encoded = urllib.urlencode(get_data)

                request_object = urllib2.Request(url + '?' + get_data_encoded)
                
                try:
                    response = urllib2.urlopen(request_object)
                except urllib2.HTTPError, e:
                    self.logger.error('HTTPError = ' + str(e.code))
                except urllib2.URLError, e:
                    self.logger.error('URLError = ' + str(e.reason))

                self.logger.info(response.read())  # Show the response

            else:
                self.logger.error('Unknown message received - Aborting. Message:')
                msg.dump()

                #sys.exit(1)

