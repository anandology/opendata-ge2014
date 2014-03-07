"""Module to parse the list of ACs and PCs from wikipedia page.

https://en.wikipedia.org/wiki/List_of_Constituencies_of_the_Lok_Sabha
"""
import sys, re
import urllib2
from . import cache
from bs4 import BeautifulSoup


WP_URL = "https://en.wikipedia.org/wiki/List_of_Constituencies_of_the_Lok_Sabha"

@cache.disk_memoize("cache/wp.html")
def get_wp_page():
    return urllib2.urlopen(WP_URL).read()

@cache.disk_memoize("cache/table_{0}.json")
def get_table_for_state(state):
    """Parses the wikipedia html page for LS constituencies and returns the table below the state heading.

    The value of state should exactly match the heading on the wikipedia page.

    Example Usage:

        ap = get_table_for_state("Andhra Pradesh")
        dh = get_table_for_state("NCR of Delhi")
    """
    soup = BeautifulSoup(get_wp_page(), "lxml")
    table = soup.find("a", text=state).find_next("table")
    data = [[td.get_text() for td in tr.find_all("td")] for tr in table.find_all("tr")]
    # skip header
    data = data[1:]
    return data

@cache.disk_memoize("cache/{0}_pc.tsv")
def get_pc_list(state_name):
    """Returns the data aboout the parliamentary constituencies in the requested state.

    The return value will be an array with each element in the following format.
        ['PC01', 'name of the PC']
    """
    return [['PC{0:02d}'.format(int(row[0])), row[1].strip()] for row in get_table_for_state(state_name)]


@cache.disk_memoize("cache/{0}_ac.tsv")
def get_ac_list(state_name):
    """Returns the data aboout the assembly constituencies in the requested state.

    The return value will be an array with each element in the following format.
        ['PC01', 'AC001', 'name of the AC']
    """
    re_ac = re.compile(r" *([0-9]*[^0-9,]+)[,.]?")
    re_num = re.compile(" *(\d+)(.*)")

    for row in get_table_for_state(state_name):
        ac_names = row[3]
        names = re_ac.findall(ac_names)
        for name in names:
            m = re_num.match(name)
            if m:
                ac_code, ac_name = m.groups()
                ac_code = int(ac_code)
            else:
                ac_code = None
                ac_name = name
            ac_name = ac_name.replace(" and ", "").strip("., ")
            ac_code_str = 'AC{:03d}'.format(ac_code) if ac_code else "-"
            pc_code = int(row[0])
            pc_code_str = 'PC{:02d}'.format(pc_code)
            yield [pc_code_str, ac_code_str, ac_name]

def main():
    d = [line.strip().split("\t") for line in open(sys.argv[1])]

    if "--ac" in sys.argv:
        re_x = re.compile(",| and ")
        re_num1 = re.compile(" *(\d+)?(.*)")
        re_num2 = re.compile(r" *([0-9]*[\D]+)")

        for row in d:
            i, pcname, category, ac = row
            names = re_x.split(ac)
            #print i, pcname, names
            for name in names:
                #print name
                for name in re_num2.findall(name):
                    #print name
                    n, name = re_num1.match(name).groups()
                    name = name.strip(". ")
                    #print i, pcname, n, name
                    print "PC%02d\tAC%03d\t%s" % (int(i), int(n), name)
    else:
        for row in d:
            print "PC%02d\t%s" % (int(row[0]), row[1])
