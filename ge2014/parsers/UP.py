import re
import urllib2

from . import cache
from . import wikipedia
from bs4 import BeautifulSoup

@cache.disk_memoize("data/UP/ac.tsv")
def get_acs():
    return wikipedia.get_ac_list("Uttar Pradesh")

@cache.disk_memoize("data/UP/pc.tsv")
def get_pcs():
    return wikipedia.get_pc_list("Uttar Pradesh")

def main():
    cache.setup_logger()
    get_acs()
    get_pcs()

if __name__ == '__main__':
    main()