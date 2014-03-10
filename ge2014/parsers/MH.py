"""Parser for Haryana
"""
import urllib, urllib2

from . import cache
from . import wikipedia

from bs4 import BeautifulSoup

BASE_URL = "https://ceo.maharashtra.gov.in/Search/SearchPDF.aspx"

def submit_form(url, params, html=None):
    html = html or urllib2.urlopen(url)
    soup = BeautifulSoup(html)
    
    params['__EVENTVALIDATION']  = soup.find("input", {"name": "__EVENTVALIDATION"})['value']
    params['__VIEWSTATE'] = soup.find("input", {"name": "__VIEWSTATE"})['value']

    payload = urllib.urlencode(params)
    return urllib2.urlopen(url, payload).read()

@cache.disk_memoize("cache/MH_{1}.html")
def get_polling_booths_html(district, ac):
    print "get_polling_booths_html", district, ac
    html = submit_form(BASE_URL, {
        "ctl00$mainContent$DistrictList": district, 
        "__EVENTTARGET": "ctl00$mainContent$DistrictList"})

    html = submit_form(BASE_URL, {
        "ctl00$mainContent$DistrictList": district, 
        "ctl00$mainContent$AssemblyList": ac,
        "__EVENTTARGET": "ctl00$mainContent$AssemblyList"}, html=html)
    return html

@cache.disk_memoize("cache/MH_ac_{1}.json")
def get_polling_booths(district, ac):
    html = get_polling_booths_html(district, ac)
    soup = BeautifulSoup(html, "lxml")
    options = soup.find("select", {"name": "ctl00$mainContent$PartList"}).find_all()
    return [o.get_text() for o in options][1:]

@cache.disk_memoize("cache/MH_districts.json")
def get_districts():
    print "get_districts"
    html = urllib2.urlopen(BASE_URL).read()
    soup = BeautifulSoup(html, "lxml")
    options = soup.find("select", {"name": "ctl00$mainContent$DistrictList"}).find_all()
    return [int(o['value']) for o in options][1:]

@cache.disk_memoize("cache/MH_district_{0}.json")
def get_district_acs(district):
    print "get_districts_acs", district
    html = submit_form(BASE_URL, {
        "ctl00$mainContent$DistrictList": district, 
        "__EVENTTARGET": "ctl00$mainContent$DistrictList"})
    soup = BeautifulSoup(html, "lxml")    
    options = soup.find("select", {"name": "ctl00$mainContent$AssemblyList"}).find_all()
    return [int(o['value']) for o in options][1:]

@cache.disk_memoize("data/MH/polling_booths.tsv")
def get_all_polling_booths():
    for district in get_districts():
        for ac in get_district_acs(district):
            for pb in get_polling_booths(district, ac):    
                number, name = pb.split("-", 1)
                yield ["AC{0:03d}".format(ac), "PB{0:04d}".format(int(number)), name.strip().encode('utf-8')]

@cache.disk_memoize("data/MH/ac.tsv")
def get_acs():
    return wikipedia.get_ac_list("Maharashtra")

@cache.disk_memoize("data/MH/pc.tsv")
def get_pcs():
    return wikipedia.get_pc_list("Maharashtra")
