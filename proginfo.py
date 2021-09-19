#!/usr/bin/python3

import sys, getopt
from sys import argv
import zipfile
import re

# parse command line options

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hip', ['offset='])
except getopt.GetoptError as err:
    print("proginfo [-h] [-i] [-p] [--offset pos[,pos2,..]] program_file")
    sys.exit(0)

show_program_name = True
show_program_info  = True
offsets = []
for opt, arg in opts:
    if opt == "-p":
        show_program_name = False
    elif opt == "-i":
        show_program_info = False
    elif opt == "-h":
        print("proginfo [options] program_file")
        print("Options:")
        print(" -h help")
        print(" -p omit printing the program name")
        print(" -i omit printing default program information")
        sys.exit()
    elif opt == "--offset":
        offsets_args = arg.split(',')
        for x in offsets_args:
            if x.isdigit():
                offsets.append((int(x), ''))
            else:
                num_opt = re.match('(\d+)([a-z])', x)
                if len(num_opt.group(1)) == 0:
                    print("offset must be a number")
                    sys.exit(0)
                offsets.append((int(num_opt.group(1)), num_opt.group(2)))
        if not (all(map(lambda x:x[0] in range (0, 336), offsets))):
            print("offset must be 0..335")
            sys.exit(0)

# read input

try:
    zipped = zipfile.ZipFile(args[0], mode='r')
except zipfile.BadZipfile:
    raise ValueError("Bad file format %s" % args[0])

with zipped as f:
    rawdata = f.read('Prog_%03d.prog_bin'  % 0)

if len(rawdata) != 336:
    raise ValueError("Bad file format (invalid length) %s" % args[0])

if rawdata[0:4] != b'PROG':
    raise ValueError("Bad file format (invalid signature) %s" % args[0])

# print out

voice_mode_prologue = ['POLY', 'MONO', 'UNISON', 'CHORD']
vco_wave = ['SQR', 'TRI', 'SAW']
multi_type = ['NOISE', 'VPM', 'USER']
result = []
if show_program_name:
    result.append(rawdata[4:16].decode().replace("\x00", ''))
if show_program_info:
    result.append(voice_mode_prologue[rawdata[80+6]])
    result.append(vco_wave[rawdata[80+10]])
    result.append(vco_wave[rawdata[80+19]])
    result.append(multi_type[rawdata[80+29]])
if len(offsets) > 0:
    for pos, opt in offsets:
        if opt == 'd':
            value = int.from_bytes(rawdata[pos:pos+2], byteorder='little')
        else:
            value = rawdata[pos]
        if opt == 'x':
            result.append(hex(value))
        elif opt == 'c':
            result.append(chr(value))
        elif opt == 's':
            result.append(rawdata[pos:pos+12].decode().replace("\x00",''))
        elif opt == '' or opt == 'd':
            result.append(str(value))
        else:
            print(" offset '%d%s' not recognized" % (pos, opt))
            sys.exit()
print("\t".join(result))
sys.exit()
