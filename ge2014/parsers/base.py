import re
import urllib2

from . import cache
from . import wikipedia
from bs4 import BeautifulSoup

class BaseParser:
    # subclasses should set these
    STATE = None
    CODE = None

    @cache.disk_memoize("data/{0.CODE}/ac.tsv")
    def get_acs(self):
        return wikipedia.get_ac_list(self.STATE)

    @cache.disk_memoize("data/{0.CODE}/pc.tsv")
    def get_pcs(self):
        return wikipedia.get_pc_list(self.STATE)

    def main(self):
        cache.setup_logger()
        self.get_acs()
        self.get_pcs()
