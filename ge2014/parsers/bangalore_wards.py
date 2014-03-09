import urllib2
from . import cache
from bs4 import BeautifulSoup
import web

@cache.disk_memoize("cache/bangalore_ward_{0}.html")
def download_ward(number):
    url = "http://www.vigeyegpms.in/bbmp/?module=public&action=wardinfo&wardid={}".format(number)
    return urllib2.urlopen(url).read()

def parse_ward(number):
    html = download_ward(number)
    soup = BeautifulSoup(html, "lxml")
    th = soup.find("th", {"colspan": "2"})
    title = th.get_text()
    print title
    table = th.parent.parent
    data = [[td.get_text() for td in tr.find_all("td")] for tr in table.find_all("tr")]

    d = {'Ward Name': title, 'Ward Number': web.numify(title)}
    for row in data:
        if len(row) == 2:
            d[row[0].strip(": ")] = row[1].strip()
    return d

@cache.disk_memoize("cache/bangalore_wards.tsv")
def parse_all():
    keys = ['Ward Number', 'Ward Name', 'Category', 'Assembly Constituency', 'Corporator Name', 'Population', 'Male', 'Female', 'Localities in the ward'] 
    yield keys
    for i in range(1, 199):
        d = parse_ward(i)
        yield [d[k].encode('utf-8') for k in keys]

def main():
    parse_all()

if __name__ == "__main__":
    cache.setup_logger()
    print parse_all()
