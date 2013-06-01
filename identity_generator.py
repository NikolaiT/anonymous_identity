import socks
import urllib.request
import urllib.error
import re
import lxml.html
import time

### Author: Nikolai Tschacher
### Site: incolumitas.com
### 30.05.2013

# Read that: http://lxml.de/parsing.html#parsing-html

COUNTRY_CODES = ['as', 'au', 'bg', 'ca', 'cyen', 'cygk', 'dk', 'fi',
                'fr', 'gr', 'hu', 'is', 'it', 'nl', 'no', 'pl', 'sl',
                 'sp', 'sw', 'sz', 'uk', 'us']
NAMESET_CODES = [ 'ar', 'au', 'ch', 'dk', 'en', 'er', 'fa', 'fi', 'fr',
                 'gd', 'gr', 'hr', 'hu', 'ig', 'is', 'it', 'jp',
                 'jpja', 'nl', 'pl', 'sl', 'sp', 'sw', 'us', 'vn', 'zhtw']
                 
FAKENAME_GENERATOR_URL = 'http://fakenamegenerator.com/gen-{0}-{1}-{2}.php'

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
       fakenamegenerator.com. When successful, returns a list of
       tuples, each tuple containing the element name (such as
       "name", "birthdate" ...) and its value. Otherwise, return
       False.
       
       Keyword arguements:
       country_code -- The country where the fake identy is from.
       nameset_code -- Where the name originates from.
       sex -- The gender. m for male, f for female.
       
    """
    try:
        s = {'m' : 'male', 'f': 'female'}[sex]
    except KeyError as e:
        print('argument sex is invalid. Either f for female or m for male.')
        return False
        
    # Build our litte HTTP request. fakenamegenerator.com insits on playing
    # the sorehead, therefore we need to forge a normal looking browser request 
    # with acting like we have a browserlike UA.
    # Common UAs?
    # => http://techblog.willshouse.com/2012/01/03/most-common-user-agents/
    build_url = FAKENAME_GENERATOR_URL.format(s, nameset_code, country_code)
    request = urllib.request.Request(build_url)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1'
						'; WOW64) AppleWebKit/537.31 (KHTML, like Gecko)'
									'	Chrome/26.0.1410.64 Safari/537.31')
    request.add_header('Accept', 'text/html,application/xhtml+xml,'
									'application/xml;q=0.9,*/*;q=0.8')

    identity = []
    
    try:
        # Pass a file like object to the parser. This one liner
        # openes the http connection and parses the whole html file in a 
        # etree object. Kinda straightforward.
        dom = lxml.html.parse(urllib.request.urlopen(request)).getroot()
        # Find the <div class="address"> element in the html source and
        # parse the identity name and the address.
        e = dom.find_class('address')
        for i in e[0].iterchildren():
            if i.tag == 'h3':
                identity.append(('full_name', i.text.strip()))
            if i.tag == 'div':
                identity.append(('address', i.text.strip()))
        # Get the phone number.
        identity.append(('phone_number', 
                    dom.find_class('tel')[0].getchildren()[0].text.strip()))
        
        # Now it's getting increasingly complicated because we don't have any good 
        # needles to extract the elements we are interested in. We have to partly work around
        # with indices which itself is prone for errors, because whenver the order of 
        # the elements which constitute the identity, or the class name of the div containers
        # holding the information changes, we have to alter the parsers functionality.
        
        # All elements of interest are in the <div class=extra>.
        id_elements = []
        for i in dom.find_class('extra')[0].find_class('lab'):
            n = i.getnext()
            if n.tag == 'li':
                id_elements.append(n.text)
        
        # Clean the list from None elements.
        id_elements = [x.strip() for x in id_elements if x is not None]
        
        # Now harvest the generated identity entities. Please keep in 
        # mind that you can appened others pieces of information that
        # remains in the id_elements list to your identity list. For example:
        # username, password, visa, generated credit card number...
        identity.append(('mother_maiden_name', id_elements[2]))
        # Chop the parentheses, no need for them.
        identity.append(('birthdate', id_elements[3][:id_elements[3].index(' (')]))
        identity.append(('blood_group', id_elements[13]))
        
        # For the weight and height, use the International System of Units
        # A weight looks like: "210.3 pounds (95.6 kilograms)", we transform it with
        # some regular expression magic into "95.6 kilograms". Similar with the height.
        r = re.compile('\((.+)\)')
        identity.append(('weight', r.search(id_elements[14]).group(0)[1:-1]))
        identity.append(('height', r.search(id_elements[15]).group(0)[1:-1]))
        
        return identity
        
    # Some connection error, either server or client side.
    except urllib.error.HTTPError as err:
        print('HTTP Error: ', err.code)
    # The URL is apparently invalid.
    except urllib.error.URLError as err:
        print('URL Error: ', err.code)
    # Catching lxml specific errors and other exceptions. Doesn't 
    # catch SystemExit and KeyboardInterrupt exceptions though.
    except Exception as e:
        print('Some error occured while lxml tried to parse.', e.args[0])
 

def anon_identity():
    """This function is a example how to use scrape_identity() anonymously
       through TOR. Used like that, you don't have to worry that your generated
       identity is matched to your IP address and therefore to your real identity.
       
    """
    
    # Set up a socks socket. You might want to fire up your local TOR PROXY, before
    # using this function.
    # Just download TOR here https://www.torproject.org/ and then start tor.
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,'127.0.0.1', 9050)
    socks.wrapmodule(urllib.request)
    
    id = scrape_identity()
    print('[+] Generated a random and anonymous identity:')
    for e in id:
        print('\t{0:.<20}{1}'.format(e[0], e[1]))
        
if __name__ == '__main__':
    anon_identity()
