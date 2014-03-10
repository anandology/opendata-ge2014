from . import cache
from . import wikipedia

@cache.disk_memoize("data/KA/ac.tsv")
def get_acs():
    return wikipedia.get_ac_list("Karnataka")

@cache.disk_memoize("data/KA/pc.tsv")
def get_pcs():
    return wikipedia.get_pc_list("Karnataka")

def main():
    print "main"
    cache.setup_logger()
    get_acs()
    get_pcs()

if __name__ == '__main__':
    main()