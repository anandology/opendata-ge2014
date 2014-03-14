import re
import urllib2

from . import cache
from . import wikipedia
from bs4 import BeautifulSoup

STATE = "Gujarat"

@cache.disk_memoize("data/GJ/ac.tsv")
def get_acs():
    return wikipedia.get_ac_list(STATE)

@cache.disk_memoize("data/GJ/pc.tsv")
def get_pcs():
    return wikipedia.get_pc_list(STATE)

def main():
    cache.setup_logger()
    get_acs()
    get_pcs()

if __name__ == '__main__':
    main()