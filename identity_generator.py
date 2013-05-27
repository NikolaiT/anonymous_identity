import socks
import urllib.request
import re
import lxml.html

# Read that: http://lxml.de/parsing.html#parsing-html

COUNTRY_CODES = ['as', 'au', 'bg', 'ca', 'cyen', 'cygk', 'dk', 'fi',
                'fr', 'gr', 'hu', 'is', 'it', 'nl', 'no', 'pl', 'sl',
                 'sp', 'sw', 'sz', 'uk', 'us']
NAMESET_CODES = [ 'ar', 'au', 'ch', 'dk', 'en', 'er', 'fa', 'fi', 'fr',
                 'gd', 'gr', 'hr', 'hu', 'ig', 'is', 'it', 'jp',
                 'jpja', 'nl', 'pl', 'sl', 'sp', 'sw', 'us', 'vn', 'zhtw']

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
        print('Some HTTP connection error occured: ', e.args[0])


def scrape_identity(sex='m', country_code='us', nameset_code='us'):
    """Scrapes a randomly generated fake identity as given by 
       fakenamegenerator.com.
       
       Keyword arguements:
       country_code -- The country where the fake identy is from.
       nameset_code -- Where the name originates from.
       sex -- The gender. m for male, f for female.
       
    """
    try:
        s = {'m' : 'male', 'f': 'female'}[sex]
    except KeyError as e:
        print('argument sex is invalid. Either f for female or m for male')
        return
        
    # Build our litte HTTP request. fakenamegenerator.com insits on playing
    # the sorehead, because we need to forge a normal looking browser request.
    # Common UAs?
    # => http://techblog.willshouse.com/2012/01/03/most-common-user-agents/
    build_url = 'http://fakenamegenerator.com/gen-{0}-{1}-{2}.php'.format(s, nameset_code, country_code)
    request = urllib.request.Request(build_url)
    request.add_header('User-Agent',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')

    try:
        f = urllib.request.urlopen(request)
        html = f.read().decode('utf-8')

    except HTTPError as err:
        if err.code != 404:
            print('HTTP Error:',err.code)
    except URLError as err:
        print('HTTP Error:',err.code)
        
    try:
		dom = lxml.html.fromstring(html)
		links = dom.cssselect('a')
	except:
		print('Some error occured while lxml tried to parse')
		sys.exit(1)
            
if __name__ == '__main__':
    scrape_identity()
