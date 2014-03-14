from . import cache
from . import wikipedia

class BaseParser:
    # subclasses should set these
    STATE = None
    CODE = None

    def __init__(self, state=None, code=None):
        self.state = state or self.STATE
        self.code = code or self.CODE

    @cache.disk_memoize("data/{0.code}/ac.tsv")
    def get_acs(self):
        return wikipedia.get_ac_list(self.state)

    @cache.disk_memoize("data/{0.code}/pc.tsv")
    def get_pcs(self):
        return wikipedia.get_pc_list(self.state)

    def main(self):
        cache.setup_logger()
        self.get_acs()
        self.get_pcs()

def main(state, code):
    p = BaseParser(state, code)
    p.main()

def download_simple_states():
    main("Kerala", "KL")
    main("Gujarat", "GJ")
    main("Madhya Pradesh", "MP")
    main("Odisha", "OR")
    main("Punjab", "PB")
    main("Rajasthan", "RJ")

if __name__ == "__main__":
    import sys
    if "--all" in sys.argv:
        download_simple_states()
    else:
        code = sys.argv[1]
        state = sys.argv[2]
        main(state, code)