import requests
import netifaces

gws = netifaces.gateways()


for key in gws['default']:
    print(gws['default'][key][0])
print(gws)

router_ip = 'http://'+gws['default'][2][0]
print(router_ip)
auth_token='Authorization=Basic%B2485588-A02E-4A9D-BAE7-3FB20E64EF9F%3D'

def login():
    r = requests.get(router_ip +'/login#goto=%2Fdashboard', {'login': 'evgen', 'password': 'Juli2307'})#'/userRpm/LoginRpm.htm?Save=Save',headers={'Referer':router_ip+'/'})
    print(router_ip+'/login#goto=%2Fdashboard')
    print(r.status_code)
    if r.status_code==200:
        x=1
        while x<3:
            try:
                print("Good!")
                session_id=r.text[r.text.index(router_ip)+len(router_ip)+1:r.text.index('userRpm')-1]
                print(session_id)
                print("Session id")
                return session_id
                break
            except ValueError:
                return 'Login error'
            x+=1
    else:
        return 'IP unreachable'
    
login()