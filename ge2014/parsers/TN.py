import re
import urllib2

from . import cache
from . import wikipedia
from bs4 import BeautifulSoup

@cache.disk_memoize("data/TN/ac.tsv")
def get_acs():
    return wikipedia.get_ac_list("Tamil Nadu")

@cache.disk_memoize("data/TN/pc.tsv")
def get_pcs():
    return wikipedia.get_pc_list("Tamil Nadu")
