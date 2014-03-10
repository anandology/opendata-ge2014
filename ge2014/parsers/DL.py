from . import cache
from . import wikipedia

@cache.disk_memoize("data/DL/ac.tsv")
def get_acs():
    return wikipedia.get_ac_list("NCT of Delhi")

@cache.disk_memoize("data/DL/pc.tsv")
def get_pcs():
    return wikipedia.get_pc_list("NCT of Delhi")

def main():
    cache.setup_logger()
    get_acs()
    get_pcs()

if __name__ == '__main__':
    main()
