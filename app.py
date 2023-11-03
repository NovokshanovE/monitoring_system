
from icmplib import *
from time import sleep
import requests
import netifaces
from pprint import pprint
import sys
import subprocess 
import asyncio
from datetime import datetime
import yaml

class Device:
    
    def __init__(self, address='192.168.1.1'):
        self.address = address
        self.id = PID
        self.timeout = 2
    def ping(self, count=4, interval=1, timeout=2, id=PID):
        print(f'PING {self.address}: 56 data bytes\n')
        if is_ipv6_address(self.address):
            sock = ICMPv6Socket()
        else:
            sock = ICMPv4Socket()
        for sequence in range(count):
            request = ICMPRequest(
                destination=self.address,
                id=id,
                sequence=sequence)
            try:
                sock.send(request)
                reply = sock.receive(request, timeout)
                print(f'  {reply.bytes_received} bytes from '
                    f'{reply.source}: ', end='')
                reply.raise_for_status()

                round_trip_time = (reply.time - request.time) * 1000

                print(f'icmp_seq={sequence} '
                    f'time={round(round_trip_time, 3)} ms')

                if sequence < count - 1:
                    sleep(interval)

            except TimeoutExceeded:
                
                print(f'  Request timeout for icmp_seq {sequence}')
                return False

            except ICMPError as err:
                print(err)
                return False

            except ICMPLibError:
                print('  An error has occurred.')
                return False

        print('\nCompleted.')
        return True
class Network:
    def __init__(self):
        self.count = 4
        self.timeout = 2
        self.interval = 1
        self.devices = []
        self.fails = []
        
    def readSettingsFile(self, f_name = 'settings.yaml'):
        with open('info.yaml') as f:
            templates = yaml.safe_load(f)
        self.count = templates['count']
        self.timeout = templates['timeout']
        self.interval = templates['interval']
        self.mail = templates['mail']
        self.number_fail_connection = templates['number_fail_connection']

    def setTimeout(self, timeout):
        self.timeout = timeout

    def setInterval(self, interval):
        self.interval = interval
    def setCount(self, count):
        self.count = count

    def addDevice(self, address):
        device = Device(address=address)
        self.devices.append(device)

    def search_devices(self):
        return ['192.168.1.1', '192.168.1.15', '192.168.1.11']
    
    def customize_network(self):
        for addr in self.search_devices():
            self.addDevice(addr)
    
    def start(self):
        while(True):
            for d in self.devices:
                self.start_ping(d)

    def start_ping(self, device):
        result =  device.ping(count=self.count, interval=self.interval, timeout=self.interval)
        if(result == False):
           self.sendMail()
        with open('log.txt', 'a') as f:
            f.write(f'time: {datetime.now()} ip_address: {device.address} status: {result}\n')
    def sendMail(self):
        print("<<<SENDING MAIL>>>")
    

def main():
    data = subprocess.check_output(['arp','-a']).decode('utf-8').split('\n') 
    network = Network()
    network.customize_network()
    network.start()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    #main()
    
