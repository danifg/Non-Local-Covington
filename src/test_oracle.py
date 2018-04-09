"""
This script aims at verifying the implementation of transition
systems with the most straightforward code possible. This script
shouldn't be run manually, but should instead be invoked by
test_oracle.sh.
"""

import sys
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('filein', type=str, help="Input CONLL file")
parser.add_argument('fileout', type=str, help="Output oracle sequence file")
parser.add_argument('--transsys', type=str, choices=['Cov', 'NCov', 'Cov2', 'Cov3'], help="Transition system to use", default="Cov")

args = parser.parse_args()

"""
This function blindly follows the given oracle sequence with an
implementation as obvious as possible, without any considerations
about pre- or post-conditions. The goal is to verify that the
transition systems are generating sequences that achieve the gold
parse, as well as being more interpretable by humans.
"""
def processlines(lines, fout):
    list1 = [0]
    list2 = []
    Nwords = 0
    for t in lines:
        if args.transsys in ['ASw', 'AER', 'AES']:
            if t[0] == 'Shift' or t[0] == 'Right-Arc':
                Nwords += 1
        elif args.transsys in ['ASd', 'AH', 'Cov', 'NCov', 'Cov2', 'Cov3']:
            if t[0] ==  'Shift':
                Nwords += 1

    buf = [i+1 for i in xrange(Nwords)]
    
    parent = [-1 for i in xrange(Nwords + 1)]
    output = ["" for i in xrange(Nwords + 1)]

    pos = ["" for i in xrange(Nwords + 1)]

    for t in lines:
        
        j = None if len(buf) == 0 else buf[0]
        if args.transsys in ['Cov']:
            if t[0] == 'Left-Arc':
                n = len(list1)-1
                relation = t[1]
                parent[list1[n]] = j
                output[list1[n]] = "%d\t%s" % (j, relation)
                list2 = [list1[n]]+list2 
                list1 = list1[:n]
            elif t[0] == 'Right-Arc':
                n = len(list1)-1
                relation = t[1]
                parent[j] = list1[n]
                output[j] = "%d\t%s" % (list1[n], relation)
                list2 = [list1[n]]+list2 
                list1 = list1[:n]
            elif t[0] == 'Shift':# or len(list1) == 1:
                pos[j] = t[1]
                list1 = list1 + list2 + [j]
                list2 = []
                buf = buf[1:]
            elif t[0] == 'NoArc':
                n = len(list1)-1
                list2 = [list1[n]]+list2 
                list1 = list1[:n]
        elif args.transsys in ['NCov']:
            if t[0] == 'Left-Arc':
                si = int(t[1]) - 1
                n = len(list1)-1
                relation = t[2]
                parent[list1[n-si]] = j
                output[list1[n-si]] = "%d\t%s" % (j, relation)
                list2 = list1[(n-si):]+list2 
                list1 = list1[:(n-si)]
            elif t[0] == 'Right-Arc':
                si = int(t[1]) - 1
                n = len(list1)-1
                relation = t[2]
                parent[j] = list1[n-si]
                output[j] = "%d\t%s" % (list1[n-si], relation)
                list2 = list1[(n-si):]+list2 
                list1 = list1[:(n-si)]
            elif t[0] == 'Shift':# or len(list1) == 1:
                pos[j] = t[1]
                list1 = list1 + list2 + [j]
                list2 = []
                buf = buf[1:]  
        elif args.transsys in ['Cov2']:
            if t[0] == 'Left-Arc':
                n = len(list1)-1
                relation = t[2]
                parent[list1[n]] = j
                output[list1[n]] = "%d\t%s" % (j, relation)
                list2 = [list1[n]]+list2 
                list1 = list1[:n]
            elif t[0] == 'Right-Arc':
                n = len(list1)-1
                relation = t[2]
                parent[j] = list1[n]
                output[j] = "%d\t%s" % (list1[n], relation)
                list2 = [list1[n]]+list2 
                list1 = list1[:n]
            elif t[0] == 'Shift':# or len(list1) == 1:
                pos[j] = t[1]
                list1 = list1 + list2 + [j]
                list2 = []
                buf = buf[1:]
            elif t[0] == 'NoArc':
                n = len(list1)-1
                list2 = [list1[n]]+list2 
                list1 = list1[:n] 
                
        elif args.transsys in ['Cov3']:
            if t[0] == 'Left-Arc':
                si = int(t[1]) - 1
                n = len(list1)-1
                relation = t[2]
                parent[list1[n-si]] = j
                output[list1[n-si]] = "%d\t%s" % (j, relation)
                list2 = list1[(n-si):]+list2 
                list1 = list1[:(n-si)]
            elif t[0] == 'Right-Arc':
                si = int(t[1]) - 1
                n = len(list1)-1
                relation = t[2]
                parent[j] = list1[n-si]
                output[j] = "%d\t%s" % (list1[n-si], relation)
                list2 = list1[(n-si):]+list2 
                list1 = list1[:(n-si)]
            elif t[0] == 'Shift':# or len(list1) == 1:
                pos[j] = t[1]
                list1 = list1 + list2 + [j]
                list2 = []
                buf = buf[1:]
            elif t[0] == 'NoArc':
                n = len(list1)-1
                list2 = [list1[n]]+list2 
                list1 = list1[:n]                           

    if "" in output[1:]:
        print "\n".join(["\t".join(x) for x in lines])
        print "\n".join(["%s\t%s" % (x=='', x) for x in output[1:]])
    fout.write("%s\n\n" % ("\n".join("\t".join(t) for t in zip(pos[1:], output[1:]))))

lines = []

fout = open(args.fileout, 'w')
with open(args.filein, 'r') as fin:
    line = fin.readline()
    while line:
        line = line.strip().split()

        if len(line) == 0:
            processlines(lines, fout)
            lines = []
        else:
            lines += [line]

        line = fin.readline()

    if len(lines) > 0:
        processlines(lines, fout)

fout.close()
