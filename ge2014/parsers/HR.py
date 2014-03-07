"""Parser for Haryana
"""
import re
import urllib2

from . import cache
from . import wikipedia
from bs4 import BeautifulSoup

@cache.disk_memoize("cache/HR/{0}.html")
def _get_polling_booths_html(ac_number):
    url = "http://ceoharyana.nic.in/directs/check_pfofile1.php?Type=ac&ID={}".format(ac_number)
    return urllib2.urlopen(url).read()

@cache.disk_memoize("cache/HR/{}.json")
def _get_polling_booths(ac_number):
    html = _get_polling_booths_html(ac_number)
    soup = BeautifulSoup(html, "lxml")
    options = soup.find_all("option")

    # Skip "--Select a PS--""
    options = options[1:]

    rx = re.compile("(.*)\((\d+)\)")
    for o in options:
        name, code = rx.match(o.get_text()).groups()
        yield int(code), name

@cache.disk_memoize("cache/HR/dist_{0}.html")
def _download_ac_listing(district_id):
    url = "http://ceoharyana.nic.in/directs/check_pfofile1.php?Type=dist&ID={0}".format(district_id)
    return urllib2.urlopen(url).read()

@cache.disk_memoize("cache/HR/ac_data.tsv")
def _get_ac_data():
    for i in range(1, 22):
        html = _download_ac_listing(i)
        soup = BeautifulSoup(html, "lxml")

        options = soup.find_all("option")

        # Skip "--Select An AC--""
        options = options[1:]

        for o in options:
            code, name = o.get_text().split("-", 1)
            yield int(code), name.strip()

re_vowels = re.compile("[aeiou ]")
def find_nearest(name, names):
    """Returns the string in given list of names that is nearest to the given name.
    """
    if name in names:
        return names

    def normalize_name(name):
        return re_vowels.sub("", name)

    # try with just consonents to handle vowel variations
    d = dict((normalize_name(n), n) for n in names)
    if normalize_name(name) in d:
        return d[normalize_name(name)]

    # sort all consonants 
    def normalize_name(name):
        return "".join(sorted(set(re_vowels.sub("", name))))
    d = dict((normalize_name(n), n) for n in names)
    if normalize_name(name) in d:
        return d[normalize_name(name)]

    raise Exception("Unable to find a nearest match for {0!r}".format(name))


@cache.disk_memoize("data/HR/ac.tsv")
def get_acs():
    """The wikipedia page doesn't have AC numbers. We need to get them from
    ceoharyana website and match them with wikipedia for pc codes.
    """
    data = wikipedia.get_ac_list("Haryana")
    def normalize_name(name):
        name = name.split("(")[0].lower().strip(". ")
        return name

    pc_dict = dict((normalize_name(name), pc_code) for pc_code, ac_code, name in data)

    renames = {
        "ambala cantt": "ambala cantonment",
        "dadri": "charkhi dadri",
        "kalawali": "kalanwali",
        "nangal chaudhry": "nagai chaudhry",
    }
    def get_pc_code(name):
        name = normalize_name(name)
        name = renames.get(name, name)
        if name not in pc_dict:
            name = find_nearest(name, pc_dict.keys())
        return pc_dict[name]

    ac_data = _get_ac_data()
    assert(len(pc_dict) == len(ac_data))
    for code, name in ac_data:
        pc_code = get_pc_code(name)
        ac_code_str = "AC{0:03d}".format(int(code))
        yield pc_code, ac_code_str, name.title().replace("(Sc)", " (SC)").replace("(St)", " (ST)")

@cache.disk_memoize("data/HR/pc.tsv")
def get_pcs():
    return wikipedia.get_pc_list("Haryana")

@cache.disk_memoize("data/HR/polling_booths.tsv")
def get_all_polling_booths():
    for ac_number, ac_name in _get_ac_data():
        booths = _get_polling_booths(ac_number)
        for code, name in booths:
            ac_code = "AC{0:03d}".format(int(ac_number))
            yield ac_code, "PB{:04d}".format(code), name
    