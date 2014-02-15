"""Script to parse the table from wikipedia entry and generate ac.txt and pc.txt files.
"""
import sys, re

d = [line.strip().split("\t") for line in open(sys.argv[1])]

if "--ac" in sys.argv:
    re_x = re.compile(",| and ")
    re_num1 = re.compile(" *(\d+)(.*)")
    re_num2 = re.compile(r" *([0-9]+[\D]+)")

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
