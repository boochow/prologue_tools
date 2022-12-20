#!/usr/bin/python3

import os, sys, getopt, shutil
from sys import argv
import zipfile
import tempfile

# parse command line options
try:
    opts, args = getopt.getopt(sys.argv[1:], 'nr', ['osc='])
except getopt.GetoptError as err:
    print("mnlgxd2prlog [-n] [--osc USEROSC_SLOT] file.rlgprog")
    sys.exit(0)

osc_num = -1
write_file = True
prioritize_reverb = False
for opt, arg in opts:
    if opt == "--osc":
        if arg.isdigit():
            osc_num = int(arg)
            if 1 <= osc_num <= 16:
                print("\nset user oscillator slot to %d" % osc_num)
            else:
                print("user oscillator slot must be number 1..16")
                sys.exit(0)
        else:
            print("user oscillator slot  must be number")
            sys.exit(0)
    elif opt == "-n":
        write_file = False
    elif opt == "-r":
        prioritize_reverb = True

# read input
try:
    zipped = zipfile.ZipFile(args[0], mode='r')
except zipfile.BadZipfile:
    raise ValueError("Bad file format %s" % args[0])

with zipped as f:
    rawdata = f.read('Prog_%03d.prog_bin'  % 0)

if len(rawdata) != 1024:
    raise ValueError("Bad file format (invalid length) %s" % args[0])

if rawdata[0:4] != b'PROG':
    raise ValueError("Bad file format (invalid signature) %s" % args[0])

destdir = os.path.dirname(os.path.abspath(args[0]))
destfile = os.path.splitext(os.path.basename(args[0]))[0] + ".prlgprog"
converted = destdir + '/' + destfile
if write_file:
    print ("Export to: %s" % converted)

# Initial program data

# od -v -x --endian=big Prog_000.prog_bin |cut -b 9-|tr -d ' ' | sed -e "s/^/'/g" | sed -e "s/$/'\\\/g"
newdata = bytearray.fromhex(\
'50524f47496e69742050726f6772616d'\
'0200020040ff003cb0040000ff000000'\
'000000ffff0001006601ff01ff010000'\
'000000000000000000000000000001ff'\
'01ff0100000000000000000000000000'\
'00ff00ff000000000000020100020000'\
'02000202010002000001000000000100'\
'000000000000ff0300000000ff030000'\
'00020000000000000002ff031e000000'\
'0002000000000101a8020002021c0002'\
'0264ff64ff64ff6464ffff64ff00ff00'\
'ff00ff00ff00ff00ff00000000000000'\
'0000007801010001ffffffffffff00ff'\
'00ff0000000000000201000200000200'\
'02020100020000010000000001000000'\
'00000000ff0300000000ff0300000002'\
'0000000000000002ff031e0000000002'\
'000000000101a8020002021c00020264'\
'ff64ff64ff6464ffff64ff00ff00ff00'\
'ff00ff00ff00ff000000000000000000'\
'007801010001ffffffffffff50524544'\
)

prog_info = '''<?xml version="1.0" encoding="UTF-8"?>

<prologue_ProgramInformation>
  <Programmer></Programmer>
  <Comment></Comment>
</prologue_ProgramInformation>
'''

file_info = '''<?xml version="1.0" encoding="UTF-8"?>

<KorgMSLibrarian_Data>
  <Product>prologue</Product>
  <Contents NumLivesetData="0" NumProgramData="1" NumPresetInformation="0"
            NumTuneScaleData="0" NumTuneOctData="0">
    <ProgramData>
      <Information>Prog_000.prog_info</Information>
      <ProgramBinary>Prog_000.prog_bin</ProgramBinary>
    </ProgramData>
  </Contents>
</KorgMSLibrarian_Data>
'''

# ---------- do conversion -------------

# EG INT(20) => CUTOFF EG INT(16) 
wheel_param_map = [\
                 31,  1,  3,  4,  5, \
                  6,  7,  8, 10, 11, \
                 12, 13, 14, 15, 17, \
                 18, 19, 20, 21, 22, \
                 16, 25, 26, 27, 28, \
                 29, 30, 29, 30]

# EG INT(20) => CUTOFF EG INT(16)
pedal_param_map = [\
                  0,  3,  5,  6,  7, \
                  8,  9, 10, 12, 13, \
                 14, 15, 16, 17, 19, \
                 20, 21, 22, 23, 24, \
                 16, 27, 28, 29, 30, \
                 31, 32, 31, 32]

voice_mode_prologue = ['POLY', 'MONO', 'UNISON', 'CHORD']
voice_mode_minilogue = ['', 'ARP', 'CHORD', 'UNISON', 'POLY']
vco_wave = ['SQR', 'TRI', 'SAW']
multi_type = ['NOISE', 'VPM', 'USER']
# summary
print("Info:\t%s\t" % rawdata[4:16].decode().replace("\x00", ''), end='')
print("%s\t" % voice_mode_minilogue[rawdata[21]], end='')
print("%s\t" % vco_wave[rawdata[22]], end='')
print("%s\t" % vco_wave[rawdata[28]], end='')
print("%s" % multi_type[rawdata[38]])
# patch name
newdata[4:16] = rawdata[4:16]
# octave
newdata[16] = rawdata[16]
# tempo
newdata[24:26] = rawdata[164:166]
# amp velocity
newdata[37] = rawdata[129]
# portamento mode
newdata[38] = rawdata[133]
# program level
newdata[40] = rawdata[135]
# mod effect type, speed, depth
newdata[41] = rawdata[89]
newdata[42:46] = rawdata[95:99]
newdata[46:51] = rawdata[90:95]
# micro tuning, scale, program tuning
newdata[51] = rawdata[122]
newdata[52] = rawdata[123]
newdata[53] = rawdata[124]
# transpose
newdata[54] = rawdata[150]
# ARP gate time and rate
newdata[55] = rawdata[1022]
newdata[56] = rawdata[1023]
# delay/reverb
delay_is_on = (rawdata[99] != 0)
reverb_is_on = (rawdata[105] != 0)
if delay_is_on and reverb_is_on:
    if prioritize_reverb:
        print("Warning: Both delay and reverb are ON, delay settings are ignored")
        delay_is_on = False
    else:
        print("Warning: Both delay and reverb are ON, reverb settings are ignored")
        reverb_is_on = False

if delay_is_on:
    newdata[62] = 1
    newdata[63:65] = rawdata[101:103]
    newdata[65:67] = rawdata[103:105]
    val = int.from_bytes(rawdata[151:153], byteorder='little')
    if val != 512:
        newdata[57:59] = int.to_bytes(val, 2, byteorder='little') + 1
elif reverb_is_on:
    newdata[62] = 2
    newdata[63:65] = rawdata[107:109]
    newdata[65:67] = rawdata[109:111]
    val = int.from_bytes(rawdata[153:155], byteorder='little')
    if val != 512:
        newdata[57:59] = int.to_bytes(val, 2, byteorder='little') + 1
newdata[68] = rawdata[100]
newdata[67] = rawdata[106]
# fx on/off
newdata[71] = rawdata[88]
if delay_is_on or reverb_is_on:
    newdata[72] = 1
else:
    newdata[72] = 0
# ARP
if rawdata[21] == 1:
    # voice mode == ARP
    arp_settings = ((78, 0, 1,),
                    (156, 0, 2,),
                    (234, 1, 1,),
                    (312, 1, 2,),
                    (390, 2, 1,),
                    (468, 2, 2,),
                    (546, 3, 1,),
                    (624, 3, 2,),
                    (702, 5, 1,),
                    (780, 6, 1,),
                    (858, 4, 1,),
                    (936, 5, 1,),
                    (1023, 5, 2,))
    newdata[73] = 1
    val = int.from_bytes(rawdata[19:21], byteorder='little') - 1
    for (depth, type, range) in arp_settings:
        if val <= depth:
            newdata[74] = range
            if type == 6:
                print("Warning: ARP POLY2 not supported")
                type = 5
            newdata[75] = type
            break
# portamento
newdata[80] = rawdata[17]
# voice mode depth, type
if rawdata[21] == 2:
    # chord
    val = int.from_bytes(rawdata[19:21], byteorder='little')
    if val < 69:
        # mono mode
        newdata[80+6] = 1
    else:
        # chord mode
        newdata[80+6] = 2
        val = max([1023, int((val - 69) / 68 * 73)])
        valbytes = int.to_bytes(val, 2, byteorder='little')
        newdata[80+4:80+6] = valbytes[0:2]
elif rawdata[21] == 3:
    # unison
    newdata[80+6] = 3
    newdata[80+4:80+6] = rawdata[19:21]
elif rawdata[21] == 4:
    # poly
    newdata[80+6] = 0
    newdata[80+4:80+6] = rawdata[19:21]
# vco1
newdata[80+10:80+16] = rawdata[22:28]
# vco2
newdata[80+19:80+25] = rawdata[28:34]
# sync and ring
sync_is_on = (rawdata[35] != 0)
ring_is_on = (rawdata[36] != 0)
if sync_is_on and ring_is_on:
    print("Warning: Both SYNC and RING are enabled, RING is going to be disabled.")
newdata[80+26:80+28] = rawdata[36:38]
if sync_is_on:
    newdata[80+25] = 2
elif ring_is_on:
    newdata[80+25] = 0
# multi routing, type, octave
newdata[80+28] = rawdata[131]
newdata[80+29] = rawdata[38]
newdata[80+30] = rawdata[130]
# noise
newdata[80+31] = rawdata[39]
newdata[80+34:80+36] = rawdata[42:44]
# vpm
newdata[80+32] = rawdata[40]
newdata[80+107:80+109] = rawdata[44:46]
newdata[80+109:80+111] = rawdata[50:52]
# user osc
if osc_num > 0:
    print("Warning: USER OSC is set to %d" % osc_num)
    newdata[80+33] = osc_num - 1
else:
    newdata[80+33] = rawdata[41]
# user shape, shift-shape
newdata[80+111:80+113] = rawdata[46:48]
newdata[80+113:80+115] = rawdata[52:54]
# mix level
newdata[80+38:80+44] = rawdata[54:60]
# cutoff, resonance, drive, key track, velocity
newdata[80+44:80+46] = rawdata[60:62]
newdata[80+46:80+48] = rawdata[62:64]
newdata[80+50] = rawdata[64]
newdata[80+52] = rawdata[65]
newdata[80+53] = rawdata[128]
# amp eg
newdata[80+54:80+62] = rawdata[66:74]
# eg attack, decay
newdata[80+62:80+64] = rawdata[74:76]
newdata[80+66:80+70] = b'\x00\x00\x00\x00'
# eg int, target
if rawdata[80] == 0:
    # EG -> cutoff
    newdata[80+48:80+50] = rawdata[78:80]
    newdata[80+17:80+19] = b'\x00\x02'
elif rawdata[80] == 1:
    # EG -> Pitch2
    newdata[80+16] = 0
    newdata[80+17:80+19] = rawdata[78:80]
    newdata[80+48:80+50] = b'\x00\x02'
elif rawdata[80] == 2:
    # EG -> Pitch
    newdata[80+16] = 2
    newdata[80+17:80+19] = rawdata[78:80]
    newdata[80+48:80+50] = b'\x00\x02'
# LFO mode
newdata[80+70] = rawdata[81]
if rawdata[82] == 0:
    print("Warning: 1-shot LFO mode is used but not supported.");
if rawdata[82] == 1:
    # mode = bpm
    newdata[80+71] = 0
else:
    # mode = normal
    newdata[80+71] = 1
# LFO rate, int
newdata[80+72:80+77] = rawdata[83:88]
# pitch bend range
newdata[80+79] = rawdata[111]
newdata[80+80] = rawdata[112]
# joystick assign (+) = wheel, (-) = pedal
newdata[80+77] = wheel_param_map[rawdata[113]] + 2
newdata[80+115] = rawdata[114]
newdata[80+78] = pedal_param_map[rawdata[115]]
# vpm params
newdata[80+81] = rawdata[136]
newdata[80+83] = rawdata[137]
newdata[80+85] = rawdata[138]
newdata[80+87] = rawdata[139]
newdata[80+88] = rawdata[140]
newdata[80+91] = rawdata[141]
# user osc param
newdata[80+93] = rawdata[142]
newdata[80+95] = rawdata[143]
newdata[80+97] = rawdata[144]
newdata[80+99] = rawdata[145]
newdata[80+101] = rawdata[146]
newdata[80+103] = rawdata[147]
newdata[80+105] = rawdata[148]
newdata[80+106] = rawdata[149]
# reserved area
# these must be zero, or Prologue displays wrong parameter values
newdata[80+94] = 0
newdata[80+96] = 0
newdata[80+98] = 0
newdata[80+100] = 0
newdata[80+102] = 0
newdata[80+104] = 0
# LFO key sync, voice sync, target sync
newdata[80+116:80+119] = rawdata[125:128]
# EG legato, portament mode, portament bpm sync
newdata[80+119] = rawdata[132]

# write the converted data

if not write_file:
    sys.exit(0)

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
    tmpzip = "prlgprog.zip"
    progfile = zipfile.ZipFile(tmpzip, "w")
    progfile.write('FileInformation.xml')
    progfile.write('Prog_000.prog_info')
    progfile.write('Prog_000.prog_bin')
    progfile.close()
    shutil.copyfile(tmpzip, converted)
    os.chdir(cwd)
