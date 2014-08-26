from .mapdata import Browser
from . import cache

URL = "http://ceomadhyapradesh.nic.in/voterlist2013.aspx"

class Crawler(object):
    def __init__(self):
        self.browser = Browser(URL)

    @cache.disk_memoize("cache/MP/districts.json")
    def get_districts(self):
        return self.browser.get_select_options("ddlDistrict")

    @cache.disk_memoize("cache/MP/acs.tsv")
    def get_acs(self):
        for dist in self.get_districts():
            self.browser.select_option('ddlDistrict', dist) 
            for num, name in self.browser.get_select_options("ddlAssembly").items():
                yield [dist, num, name]

    @cache.disk_memoize("data/MP/districts.tsv")
    def get_districts_tsv(self):
        for num, name in self.get_districts().items():
            yield ["MP", "MP/DT{:0>2}".format(num), name]

    @cache.disk_memoize("data/MP/acs.tsv")
    def get_acs_tsv(self):
        for dist, num, name in self.get_acs():
            yield ["MP/DT{:0>2}".format(dist), "MP/AC{:0>3}".format(num), name]

    @cache.disk_memoize("cache/MP/AC{ac:0>3}_booths.tsv")
    def get_booths_of_ac(self, dist, ac):
        self.browser.select_option('ddlDistrict', dist)
        self.browser.select_option('ddlAssembly', ac)
        soup = self.browser.get_soup()
        rows = soup.select("#GrShow tr")
        for row in rows:
            values = [td.get_text() for td in row.select("td")]
            if not values:
                continue
            yield values[:-1] # ignore the last item, which is a link to download pdf

    @cache.disk_memoize("data/MP/polling_booths.tsv")
    def get_all_booths(self):
        for dist, ac, name in sorted(self.get_acs()):
            for num, hi_name, en_name, hi_name2, en_name2 in self.get_booths_of_ac(dist, ac):
                yield ["MP/AC{:0>3}".format(ac), "MP/AC{:0>3}/PB{:0>4}".format(ac, num), en_name2]

    @cache.disk_memoize("data/MP/polling_booths_hi.tsv")
    def get_all_booths_hi(self):
        for dist, ac, ac_name in sorted(self.get_acs()):
            for num, hi_name, en_name, hi_name2, en_name2 in self.get_booths_of_ac(dist, ac):
                name = "PB{:0>4} {}".format(num, hi_name2)
                yield ["MP/AC{:0>3}".format(ac), "MP/AC{:0>3}/PB{:0>4}".format(ac, num), name]

def main():
    cache.setup_logger()    
    c = Crawler()
    c.get_all_booths_hi()

if __name__ == "__main__":
    main()