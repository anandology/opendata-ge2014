import sys
import os
import json

def write_json_file(data):
    filename = "data/%s.json" % data['key']
    print "generating", filename
    os.system("mkdir -p " + os.path.dirname(filename))
    with open(filename, "w") as f:
        f.write(json.dumps(data, indent=True, sort_keys=True))

def write_pc(state, code, name):
    data = {
        "key": "%s/%s" % (state, code),
        "type": "PC",
        "code": code,
        "state": state,
        "name": name.decode('utf-8')
    }
    write_json_file(data)

def write_ac(state, pc, code, name):
    data = {
        "key": "%s/%s" % (state, code),
        "type": "AC",
        "code": code,
        "state": state,
        "pc": pc,
        "name": name
    }
    write_json_file(data)

def main():
    for state in os.listdir("rawdata"):
        pc_path = os.path.join("rawdata", state, "pc.txt")
        ac_path = os.path.join("rawdata", state, "ac.txt")

        if os.path.exists(pc_path):
            for line in open(pc_path):
                code, name = line.strip("\n").split("\t")
                write_pc(state, code, name)
        
        for line in open(ac_path):
            pc, code, name = line.strip("\n").split("\t")
            write_ac(state, pc, code, name)

if __name__ == "__main__":
    main()
