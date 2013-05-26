import socks
import urllib.request
import re

def test_anonymity(ip='127.0.0.1', port=9050):
    """Test the socks module and verify that the IP address is 
       concealed through checking it online. This function assumes
       that a local SOCKS5 proxy server (e.g. TOR) is running
       on 127.0.0.1:9050.
       
       Keyword arguments:
       host -- the ip address of the proxy.
       port -- the port number of the proxy.
       
    """
    # Set up a socks socket.
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, port)
    socks.wrapmodule(urllib.request)
    
    try:
        html = urllib.request.urlopen('http://checkip.dyndns.com/').read()
        return re.compile('(\d+\.\d+\.\d+\.\d+)').search(html.decode('utf-8')).group(1)
    except urllib.error.HTTPError as e:
        print('Some HTTP connection error occured: ', e.args[o])



if __name__ == '__main__':
    print('The concealed ip address is: ', test_anonymity())
