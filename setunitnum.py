#!/usr/bin/python3

import os, sys, argparse, shutil
from sys import argv
import zipfile
import tempfile

# parse command line options

parser = argparse.ArgumentParser(description='change the slot number of user units.')
parser.add_argument('--osc', metavar='OSC_NUM',
                    type=int,
                    choices=range(1,17),
                    help='user osc slot numbers (1..16)')
parser.add_argument('--mod', metavar='MOD_NUM',
                    type=int,
                    choices=range(1,17),
                    help='user mod slot numbers (1..16)')
parser.add_argument('--delay', metavar='DELAY_NUM',
                    type=int,
                    choices=range(1,8),
                    help='user delay slot numbers (1..16)')
parser.add_argument('--reverb', metavar='REVERB_NUM',
                    type=int,
                    choices=range(1,8),
                    help='user reverb slot numbers (1..16)')
parser.add_argument('filename', 
                    help='prologue program file (.prlgprog)')

args = parser.parse_args()

fbody, fext = os.path.splitext(args.filename)
converted = fbody
if args.osc != None:
    converted = converted + '_O' + str(args.osc).zfill(2)
if args.mod != None:
    converted = converted + '_M' + str(args.mod).zfill(2)
if args.delay != None:
    converted = converted + '_D' + str(args.delay).zfill(2)
if args.reverb != None:
    converted = converted + '_R' + str(args.reverb).zfill(2)
converted = converted + fext

# read input

try:
    zipped = zipfile.ZipFile(args.filename, mode='r')
except zipfile.BadZipfile:
    raise ValueError("Bad file format %s" % args[0])

with zipped as f:
    rawdata = f.read('Prog_%03d.prog_bin'  % 0)
    prog_info = f.read('Prog_000.prog_info')
    file_info = f.read('FileInformation.xml')

if not ((len(rawdata) == 336 and fext == '.prlgprog') or \
        (len(rawdata) == 1024 and fext == '.mnlgxdprog')):
    raise ValueError("Bad file format (invalid length) %s" % args[0])

if rawdata[0:4] != b'PROG':
    raise ValueError("Bad file format (invalid signature) %s" % args[0])

# new program data

newdata = bytearray(rawdata)

# change user unit numbers

if fext == '.prlgprog':
    ofs_osc, ofs_mod, ofs_delay, ofs_reverb = (80+33, 50, 68, 67)
elif fext == '.mnlgxdprog':
    ofs_osc, ofs_mod, ofs_delay, ofs_reverb = (41, 94, 100, 106)
else:
    print("Unknown file extension %s" % fext)
    sys.exit(0)

if args.osc != None:
    newdata[ofs_osc] = args.osc - 1
    print("User OSC number: %d => %d" % (rawdata[ofs_osc] + 1, newdata[ofs_osc] + 1))

if args.mod != None:
    newdata[ofs_mod] = args.mod - 1
    print("User Mod number: %d => %d" % (rawdata[ofs_mod] + 1, newdata[ofs_mod] + 1))

if args.delay != None:
    newdata[ofs_delay] = args.delay - 1
    print("User Delay number: %d => %d" % (rawdata[ofs_delay] + 1, newdata[ofs_delay] + 1))

if args.reverb != None:
    newdata[ofs_reverb] = args.reverb - 1
    print("User Reverb number: %d => %d" % (rawdata[ofs_reverb] + 1, newdata[ofs_reverb] + 1))

# write the new data

if converted == args.filename:
    print("No modification is specified.")
else:
    print ("Export to: %s" % converted)

with tempfile.TemporaryDirectory() as tmpdir:
    cwd = os.getcwd()
    with open(os.path.join(tmpdir, "FileInformation.xml"), "w") as f:
        print(file_info, file=f)
        f.close()
    with open(os.path.join(tmpdir, "Prog_000.prog_info"), "w") as f:
        print(prog_info, file=f)
        f.close()
    with open(os.path.join(tmpdir, "Prog_000.prog_bin"), 'wb') as f:
        f.write(newdata)
        f.close()
    os.chdir(tmpdir)
    tmpzip = "mnlgxdprog.zip"
    progfile = zipfile.ZipFile(tmpzip, "w")
    progfile.write('FileInformation.xml')
    progfile.write('Prog_000.prog_info')
    progfile.write('Prog_000.prog_bin')
    progfile.close()
    shutil.copyfile(tmpzip, converted)
    os.chdir(cwd)
