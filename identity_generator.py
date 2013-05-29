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
    # the sorehead, therefore we need to forge a normal looking browser request 
    # with acting like we have a browserlike UA.
    # Common UAs?
    # => http://techblog.willshouse.com/2012/01/03/most-common-user-agents/
    build_url = 'http://fakenamegenerator.com/gen-{0}-{1}-{2}.php'.format(s, nameset_code, country_code)
    request = urllib.request.Request(build_url)
    request.add_header('User-Agent',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31')
    request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8') # Maybe redundant.

    identity = {
        'full_name': '',
        'address': '',
        'gender': s,
        'birthdate': '',
        'phone_number': '',
        'mother_maiden_name': '',
        'blood_group': '',
        'height': '',
        'weight': '',
    }
    
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
                identity['full_name'] = i.text.strip()
            if i.tag == 'div':
                identity['address'] = i.text.strip()
        # Get the phone number.
        identity['phone_number'] = dom.find_class('tel')[0].getchildren()[0].text.strip()
        
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
        
        # Clean the list.
        id_elements = [x.strip() for x in id_elements if x]
        
        # Now harvest the generated identity entities.
        identity['mother_maiden_name'] = id_elements[2]
        identity['birthdate'] = id_elements[3]
        identity['blood_group'] = id_elements[13]
        identity['weight'] = id_elements[14]
        identity['height'] = id_elements[15]
        
        return identity
    except urllib.HTTPError as err:
        if err.code != 404:
            print('HTTP Error:', err.code)
    except urllib.URLError as err:
        print('HTTP Error:', err.code)
    # Catching lxml specific errors.
    except Exception as e:
        print('Some error occured while lxml tried to parse.', e[0].args)
 

def anon_identity():
    """This function is a example how to use scrape_identity() anonymously
       through TOR. Used like that, you don't have to worry that your generated
       identity is matched to your IP address and therefore to your real identity.
       
    """
    
    # Set up a socks socket. You might want to fire up your local TOR PROXY.
    # Just download TOR here https://www.torproject.org/ and then start tor.
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,'127.0.0.1', 9050)
    socks.wrapmodule(urllib.request)
    
    id = scrape_identity()
    print('[+] Generated a random and anonymous identity:')
    for e in id.keys():
        print('\t{0:.<20}{1}'.format(e, id[e]))
        
if __name__ == '__main__':
    anon_identity()
