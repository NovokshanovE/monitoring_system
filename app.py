
from icmplib import *
from time import sleep

class Device:
    
    def __init__(self, address='192.168.1.1'):
        self.address = address
        self.id = PID
        self.timeout = 2
    def ping(self):
        if is_ipv6_address(self.address):
            sock = ICMPv6Socket()
        else:
            sock = ICMPv4Socket()
        
        # We create an ICMP request
        request = ICMPRequest(
            destination=self.address,
            id=self.id,
            sequence=1)

        try:
            # We send the request
            sock.send(request)

            # We are awaiting receipt of an ICMP reply
            reply = sock.receive(request, self.timeout)

            # We received a reply
            # We display some information
            print('ping')

            # We throw an exception if it is an ICMP error message
            reply.raise_for_status()

            

            

        except TimeoutExceeded:
            # The timeout has been reached
            print(f'  Request timeout')

        except ICMPError as err:
            # An ICMP error message has been received
            print(err)

        except ICMPLibError:
            # All other errors
            print('  An error has occurred.')



def main():
    d = Device()
    for i in range(100):
        sleep(1)
        d.ping()


if __name__ == '__main__':
    main()
    
