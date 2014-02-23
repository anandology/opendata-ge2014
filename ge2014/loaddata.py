import os
import optparse
import csv
from thingdb import Thing

def read_tsv(path):
    return csv.reader(open(path), delimiter='\t')

def load_states(path):
    for code, name in read_tsv(path):
        Thing.new(code, "STATE", {"name": name})

def load_pcs(state, path):
    for code, name in read_tsv(path):
        key = state + "/" + code
        Thing.new(key, "PC", {
            "name": name,
            "state": {"key": state}
        })

def load_acs(state, path):
    for pc, code, name in read_tsv(path):
        key = state + "/" + code
        Thing.new(key, "AC", {
            "name": name,
            "state": {"key": state},
            "pc": {"key": state + "/" + pc}
        })

def load_pbs(state, path):
    for row in read_tsv(path):
        pc, ac, ward, code, name = row
        key = state + "/" + ac + "/" + code
        if not Thing.find(key):
            Thing.new(key, "PB", {
                "name": name,
                "state": {"key": state},
                "ac": {"key": state + "/" + ac},
                "pc": {"key": state + "/" + pc}
            })

def loaddata(dir):
    load_pcs(os.path.join(dir, "pc.csv"))   

def main():
    parser = optparse.OptionParser()
    parser.add_option("--load-states", action="store_true", help="load states from the file supplied")
    parser.add_option("--load-pcs", action="store_true", help="load PCs from the file supplied")
    parser.add_option("--load-acs", action="store_true", help="load ACs from the file supplied")
    parser.add_option("--load-pbs", action="store_true", help="load PBs from the file supplied")

    options, args = parser.parse_args()
    if options.load_states:
        load_states(args[0])
    elif options.load_pcs:
        load_pcs(args[0], args[1])
    elif options.load_acs:
        load_acs(args[0], args[1])
    elif options.load_pbs:
        load_pbs(args[0], args[1])

if __name__ == "__main__":
    main()
        
