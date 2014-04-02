"""Script to extract all polling booths and their coordinates.

That information is available at:
http://www.eci-polldaymonitoring.nic.in/psleci/Default.aspx
"""

import sys
import logging
import urllib, urllib2
import json

import web
from bs4 import BeautifulSoup
from . import cache

URL = "http://www.eci-polldaymonitoring.nic.in/psleci/Default.aspx"

DATA_URL = "http://www.eci-polldaymonitoring.nic.in/psleci/GService.asmx/GetGoogleObject"

HEADERS = {
    "Referer": "http://www.eci-polldaymonitoring.nic.in/psleci/Default.aspx?aspxerrorpath=%2fpsleci%2fdefault.aspx",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36"
}

logger = logging.getLogger(__name__)

class Browser(web.Browser):
    _soup = None
    def __init__(self, url=None):
        web.Browser.__init__(self)
        self.url = url or URL

    def post(self, params):
        return self.open(self.url, params)

    def get_data(self):
        if self.data is None:
            self.open(self.url)
        return self.data

    def get_soup(self):
        """Returns beautiful soup of the current document."""
        if self._soup is None:
            self._soup = BeautifulSoup(self.get_data(), "lxml")
        return self._soup

    def open(self, url, payload=None, headers=HEADERS):
        xparams = payload and dict((k, v) for k, v in payload.items() if not k.startswith("_") and v)
        logger.info("open %s %s", URL, xparams)

        if isinstance(payload, dict):
            payload = urllib.urlencode(payload)

        self._soup = None
        return web.Browser.open(self, url, payload, headers)

    def xopen(self, url):
        """Open a new URL in the with the same cookies with out changing the context.
        """
        logger.info("xopen %s", url)
        headers = dict(HEADERS)
        headers["Content-Type"] = "application/json; charset=UTF-8"


        # Adding cookie via cookiejar wasn't working for some reason.
        # Resolved it by adding cookies in the hard way.
        cookies = self.cookiejar._cookies.values()[0].values()[0].values()
        headers['Cookie'] = "; ".join(self.cookiejar._cookie_attrs(cookies))
        req = urllib2.Request(url, '', headers)
        self.cookiejar.add_cookie_header(req)

        return urllib2.urlopen(req)

    def find_select_value(self, select):
        if isinstance(select, basestring):
            select = self.get_soup().find("select", {"name": select})
        option = select.find("option", {"selected": "selected"})
        return option and option.get('value')

    def select_option(self, name, value):
        if self.find_select_value(name) == value:
            return

        params = self.read_formdata()

        params[name] = value
        params['__EVENTTARGET'] = name
        return self.post(params)

    def read_formdata(self):
        soup = self.get_soup()
        params = {}

        for s in soup.find_all("select"):
            params[s['name']] = self.find_select_value(s)

        params['GoogleMapForASPNet1$hidEventName'] = ''
        params['GoogleMapForASPNet1$hidEventValue'] = ''
        params['__EVENTARGUMENT'] = ''
        params['__LASTFOCUS'] = ''
        ev = soup.find("input", {"name": "__EVENTVALIDATION"})
        if ev:
            params['__EVENTVALIDATION']  = ev['value']
        params['__VIEWSTATE'] = soup.find("input", {"name": "__VIEWSTATE"})['value']
        return params

    def get_select_options(self, name):
        select = self.get_soup().find("select", {"name": name})
        options = select.find_all("option")
        d = dict((o['value'], o.get_text().strip()) for o in options)
        d.pop("-1", None) # remove the "--select xxx---" option
        d.pop("ALL", None) # remove the "ALL" option
        d.pop("Select", None) # remove the "Select" option
        return d

class Crawler(object):
    def __init__(self):
        self.browser = Browser()

    @cache.disk_memoize("cache/map/states.json")
    def get_states(self):
        b = self.browser
        states = b.get_select_options("ddlState")
        for code, name in states.items():
            yield {"state": code, "state_name": name}
    
    @cache.disk_memoize("cache/map/{1[state]}/districts.json")
    def get_districts(self, state):
        b = self.browser
        b.select_option("ddlState", state['state'])
        districts = b.get_select_options("ddlDistrict")
        for code, name in districts.items():
            yield dict(state, district=code, district_name=name)

    @cache.disk_memoize("cache/map/{1[state]}/district_{1[district]}_acs.json")
    def get_district_acs(self, district):
        b = self.browser
        b.select_option("ddlState", district['state'])
        b.select_option("ddlDistrict", district['district'])
        acs = b.get_select_options("ddlAC")
        for code, name in sorted(acs.items()):
            yield dict(district, ac=code, ac_name=name)

    @cache.disk_memoize("cache/map/{1[state]}/acs.json")
    def get_acs(self, state):
        b = self.browser
        for district in self.get_districts(state):
            for ac in self.get_district_acs(district):
                yield ac

    @cache.disk_memoize("cache/map/{1[state]}/AC{1[ac]}/ps.json")
    def get_polling_stations(self, ac):
        b = self.browser
        b.select_option("ddlState", ac['state'])
        b.select_option("ddlDistrict", ac['district'])
        b.select_option("ddlAC", ac['ac'])
        for code, name in sorted(b.get_select_options("ddlPS").items()):
            yield dict(ac, ps=code, ps_name=name)

    @cache.disk_memoize("cache/map/{1[state]}/AC{1[ac]}/PS{1[ps]}-info.txt")
    def get_ps_info(self, ps):
        b = self.browser
        b.select_option("ddlState", ps['state'])
        b.select_option("ddlDistrict", ps['district'])
        b.select_option("ddlAC", ps['ac'])
        b.select_option("ddlPS", ps['ps'])
        return b.xopen(DATA_URL).read()

    @cache.disk_memoize("cache/map/{1[state]}/AC{1[ac]}/PS-info.txt")
    def get_ac_info(self, ac):
        """Get lat/long of all the polling booths of an AC.
        """
        b = self.browser
        b.select_option("ddlState", ac['state'])
        b.select_option("ddlDistrict", ac['district'])
        b.select_option("ddlAC", ac['ac'])
        params = b.read_formdata()
        params['imgbtnFind.x'] = 43
        params['imgbtnFind.y'] = 23
        b.post(params)
        return b.xopen(DATA_URL).read()

    @cache.disk_memoize("cache/map/{1[state]}/AC{1[ac]}/PS-coordinates.tsv")
    def get_ps_coordinates(self, ac):
        """Returns coordinates of all available polling booths in the
        given assembly constituency.
        """
        d = json.loads(self.get_ac_info(ac))
        for p in d['d']['Points']:
            info = self._parse_infohtml(p['InfoHTML'])
            ps = dict(ac, 
                ps=info['ps'], 
                ps_name=info['ps_name'],
                longtide=p['Longitude'],
                latitude=p['Latitude'])
            yield [
                ps['state'], ps['state_name'], 
                ps['ac'], ps['ac_name'], 
                ps['ps'], ps['ps_name'],
                ps['longtide'], ps['latitude']]

    def _parse_infohtml(self, infohtml):
        soup = BeautifulSoup(infohtml.replace("<br>", "\n").replace("<br/>", ""))
        lines = soup.get_text().strip().splitlines()
        info = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                info[k.strip().lower()] = v

        num_name = info['ps no and name']
        num, name = num_name.split("-", 1)
        info['ps'] = int(num)
        info['ps_name'] = name.strip()
        return info

    @cache.disk_memoize("cache/map/{1[state]}/AC{1[ac]}/ps.tsv")
    def get_ps_info_of_ac(self, ac):
        for ps in self.get_polling_stations(ac):
            point = json.loads(self.get_ps_info(ps))['d']['CenterPoint']
            longitude = point['Longitude']
            latitude = point['Latitude']
            yield [
                "AC{0:03d}".format(int(ps['ac'])), 
                "PB{0:04d}".format(int(ps['ps'])),
                str(longitude),
                str(latitude),
                ps['ps_name']]

    @cache.disk_memoize("cache/map/{1[state]}/all-ps.tsv")
    def get_ps_coordinates_of_state(self, state):
        for ac in self.get_acs(state):
            for ps in self.get_ps_coordinates(ac):
                yield ps

    @cache.disk_memoize("cache/map/india-ps.tsv")
    def get_ps_coordinates_of_india(self):
        for state in self.get_states():
            for ps in self.get_ps_coordinates_of_state(state):
                yield ps

def get_ac_dict(state_code):
    c = Crawler()
    return dict((ac['ac'], ac) for ac in c.get_acs(state_code))

def main():
    cache.setup_logger()
    c = Crawler()
    c.get_ps_coordinates_of_india()

def main2(district_code):
    c = Crawler()
    cache.setup_logger()    
    district = {
        "district_name": "xxx",
        "state": "S01",
        "state_name": "Andhra PradeshKarnataka",
        "district": district_code
    }
    for ac in c.get_district_acs(district):
        for ps in c.get_polling_stations(ac):
            print ps
            print c.get_ps_info(ps)

def main3():
    c = Crawler()
    cache.setup_logger()
    for state in c.get_states():
        for ac in c.get_acs(state):
            for ps in c.get_polling_stations(ac):
                print ac

def main4():
    c = Crawler()
    cache.setup_logger()
    
    state = {"state": "S01", "state_name": "Andhra Pradesh"}
    c.get_ps_coordinates_of_state(state)

if __name__ == '__main__':
    #main2(sys.argv[1])
    main()
