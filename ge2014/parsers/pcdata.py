"""Script to extract code and name of all parliamentary constituencies in India from:

http://affidavitarchive.nic.in/DynamicAffidavitDisplay/FrmElectionAffidavit.aspx
"""

from . import cache
from .mapdata import Browser

URL = "http://affidavitarchive.nic.in/DynamicAffidavitDisplay/FrmElectionAffidavit.aspx"
SELECT_STATE = "ctl00$ContentPlaceHolder1$ddlState"

class Crawler:
    def __init__(self):
        self.browser = Browser(URL)

    @cache.disk_memoize("cache/pcdata/{1}.tsv")
    def parse_state(self, state, state_name):
        b = self.browser
        b.select_option(SELECT_STATE, state)
        soup = b.get_soup()
        table = soup.find('table', {"id": "ctl00_ContentPlaceHolder1_gvACPCwiseElectionHeld"})
        rows = table.find_all("tr")[1:] # first row is header, skip it.

        # take first 2 columns: number and name
        data = [[td.get_text() for td in row.find_all("td")[:2]] for row in rows]

        for pc in data:
            print pc
            yield [state, state_name, pc[0], pc[1]]

    @cache.disk_memoize("cache/pcdata/states.json")
    def get_states(self):
        return self.browser.get_select_options("ctl00$ContentPlaceHolder1$ddlState")

    @cache.disk_memoize("cache/pcdata/pcs.tsv")
    def get_all_pcs(self):
        for s, sname in sorted(self.get_states().items()):
            d = self.parse_state(s, sname)
            for row in d:
                yield row

def main():
    cache.setup_logger()

    c = Crawler()
    c.get_all_pcs()

if __name__ == '__main__':
    main()