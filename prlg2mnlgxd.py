#!/usr/bin/python3

import os, sys, getopt, shutil
from sys import argv
import zipfile
import tempfile

# parse command line options
try:
    opts, args = getopt.getopt(sys.argv[1:], 'n', ['osc='])
except getopt.GetoptError as err:
    print("prlog2mnlgxd [-n] [--osc USEROSC_SLOT] file.prlgprog")
    sys.exit(0)

osc_num = -1
write_file = True
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

converted = os.path.splitext(args[0])[0] + ".mnlgxdprog"
if write_file:
    print ("Export to: %s" % converted)

# Initial program data

newdata = bytearray.fromhex(\
'50524f47496e69742050726f6772616d'\
'02000001000402010002000002010002'\
'00000000000000000000000000000000'\
'000000000000ff0300000000ff030000'\
'000000000002ff031e00000000020002'\
'000101a80200020200010000000000ff'\
'01ff010000ff01ff010000ff01ff0102'\
'0216780c0a0004c80c00000c32010100'\
'00000100010100666464646464640000'\
'0000000000000d000200020050524544'\
'53455144b00410004b36000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000'\
'00000000000000000000000000000000')

prog_info = '''<?xml version="1.0" encoding="UTF-8"?>

<xd_ProgramInformation>
  <Programmer></Programmer>
  <Comment></Comment>
</xd_ProgramInformation>
'''

file_info = '''<?xml version="1.0" encoding="UTF-8"?>

<KorgMSLibrarian_Data>
  <Product>minilogue xd</Product>
  <Contents NumFavoriteData="0" NumProgramData="1" NumPresetInformation="0"
            NumTuneScaleData="0" NumTuneOctData="0">
    <ProgramData>
      <Information>Prog_000.prog_info</Information>
      <ProgramBinary>Prog_000.prog_bin</ProgramBinary>
    </ProgramData>
  </Contents>
</KorgMSLibrarian_Data>

'''

# ---------- do conversion -------------

wheel_param_map = [\
                 -1,  1, -1,  2,  3, \
                  4,  5,  6,  7, -1, \
                  8,  9, 10, 11, 12, \
                 13, 20, 14, 15, 16, \
                 17, 18, 19, -1, -1, \
                 21, 22, 23, 24, 25, \
                 26, 0]

pedal_param_map = [\
                 -1, -1, -1,  1, -1, \
                  2,  3,  4,  5,  6, \
                  7, 20,  8,  9, 10, \
                 11, 12, 13, 20, 14, \
                 15, 16, 17, 18, 19, \
                 -1, -1, 21, 22, 23, \
                 24, 27, 28]

voice_mode_prologue = ['POLY', 'MONO', 'UNISON', 'CHORD']
voice_mode_minilogue = ['', 'ARP', 'CHORD', 'UNISON', 'POLY']
vco_wave = ['SQR', 'TRI', 'SAW']
multi_type = ['NOISE', 'VPM', 'USER']
# summary
print("Info:\t%s\t" % rawdata[4:16].decode().replace("\x00", ''), end='')
print("%s\t" % voice_mode_prologue[rawdata[80+6]], end='')
print("%s\t" % vco_wave[rawdata[80+10]], end='')
print("%s\t" % vco_wave[rawdata[80+19]], end='')
print("%s" % multi_type[rawdata[80+29]])

# patch name
newdata[4:16] = rawdata[4:16]
# sub timbre
if rawdata[17] == 1:
    print("Warning: Sub timbre is ON, but only main timber is converted")
# octave
newdata[16] = rawdata[16]
# portamento
newdata[17] = rawdata[80]
# voice mode depth, type
if rawdata[80+6] == 3 :
    # chord
    newdata[21] = 2
    val = int.from_bytes(rawdata[80+4:80+6], byteorder='little')
    val = int(val / 73 * 68 + 70)
    valbytes = int.to_bytes(val, 2, byteorder='little')
    newdata[19:21] = valbytes[0:2]
elif rawdata[80+6] == 2:
    # unison
    newdata[21] = 3
    newdata[19:21] = rawdata[80+4:80+6]
elif rawdata[80+6] == 1:
    # mono
    newdata[21] = 2
    newdata[19:21] = (0,0)
    mod_depth = int.from_bytes(rawdata[80+4:80+6], byteorder='little')
    if mod_depth > 150:
        print("Warning: Mono mode voice depth is large value(%d)" % mod_depth)
else:
    # poly
    newdata[19:21] = rawdata[80+4:80+6]

# ARP
if rawdata[73] > 0 and rawdata[26] != 2:
    # ARP on or latch, and main timbre is targetted
    print("Warning: ARP is ON, voice mode (%s) is overwritten" % voice_mode_minilogue[newdata[21]])
    newdata[21] = 1
    # ARP type
    val = rawdata[75]
    if val < 4:
        val = val * 157
    elif val == 4:
        val = 788
    elif val == 5:
        val = 859
    # ARP range
    if rawdata[74] > 0:
        val = val + 80
    valbytes = int.to_bytes(val, 2, byteorder='little')
    newdata[19:21] = valbytes[0:2]
    # ARP gate time and rate
    newdata[1022] = rawdata[55]
    newdata[1023] = rawdata[56]
# vco1
newdata[22:28] = rawdata[80+10:80+16]
# vco2
newdata[28:34] = rawdata[80+19:80+25]
# sync and ring
newdata[36:38] = rawdata[80+26:80+28]
if rawdata[80+25] == 0:
    # ring on
    newdata[35] = 1
elif rawdata[80+25] == 2:
    # sync on
    newdata[34] = 1
# multi type
newdata[38] = rawdata[80+29]
# noise
newdata[39] = rawdata[80+31]
newdata[42:44] = rawdata[80+34:80+36]
newdata[48:50] = rawdata[80+34:80+36]
# vpm
newdata[40] = rawdata[80+32]
newdata[44:46] = rawdata[80+107:80+109]
newdata[50:52] = rawdata[80+109:80+111]
# user osc
if osc_num > 0:
    print("Warning: USER OSC is set to %d" % osc_num)
    newdata[41] = osc_num - 1
else:
    newdata[41] = rawdata[80+33]
# user shape, shift-shape
newdata[46:48] = rawdata[80+111:80+113]
newdata[52:54] = rawdata[80+113:80+115]
# mix level
newdata[54:60] = rawdata[80+38:80+44]
# cutoff, resonance, drive
newdata[60:62] = rawdata[80+44:80+46]
newdata[62:64] = rawdata[80+46:80+48]
newdata[64] = rawdata[80+50]
newdata[65] = rawdata[80+52]
if rawdata[80+51] != 0:
    print("Warning: Low cut is used but not supported.")
# amp eg
newdata[66:74] = rawdata[80+54:80+62]
# eg attack, decay
newdata[74:76] = rawdata[80+62:80+64]
sustain_level = int.from_bytes(rawdata[80+66:80+68], byteorder='little')
if sustain_level < 256:
    # sustain level is low
    newdata[76:78] = rawdata[80+64:80+66]
else:
    # if sustain lavel is high, set decay time to max
    print("Warning: EG sustain level is high(%d), decay time set to maximum value" % sustain_level)
    newdata[76:78] = b'\xff\x03'
# eg int, target
pitch_eg_int = int.from_bytes(rawdata[80+17:80+19], byteorder='little') - 512
cutoff_eg_int = int.from_bytes(rawdata[80+48:80+50], byteorder='little') - 512
if abs(cutoff_eg_int) >= abs(pitch_eg_int) :
    newdata[78:80] = rawdata[80+48:80+50]
    newdata[80] = 0
    if pitch_eg_int > 20:
        print("Warning: EG is used for cutoff mod(%d), pitch mod(%d) is ignored" % (cutoff_eg_int, pitch_eg_int))
else:
    newdata[78:80] = rawdata[80+17:80+19]
    if rawdata[80+16] < 2:
        # target VCO = (0) VCO2 or (1) VCO1+VCO2
        newdata[80] = 1
        # on minilogue xd: target VCO = VCO2
        if rawdata[80+16] == 1:
        # target VCO = VCO1+VCO2 (MULTI must be excluded)
            print("Warning: EG target is VCO1+VCO2 but set to VCO2 to exclude MULTI")
    else:
        # target VCO = ALL
        newdata[80] = 2
    if abs(cutoff_eg_int) > 20:
        print("Warning: EG is used for pitch mod(%d), cutoff mod(%d) is ignored" % (pitch_eg_int, cutoff_eg_int))
# LFO
newdata[81] = rawdata[80+70]
if rawdata[80+71] == 0:
    # mode = bpm
    newdata[82] = 2
else:
    # mode = normal
    newdata[82] = 1
    if rawdata[80+71] == 2:
        print("Warning: Fast LFO mode is used but not supported")
newdata[83:88] = rawdata[80+72:80+77]
newdata[125:128] = rawdata[80+116:80+119]
# user effect
newdata[88] = rawdata[71]
newdata[89] = rawdata[41]
newdata[94] = rawdata[50]
newdata[95:99] = rawdata[42:46]
# mod effect
newdata[90:94] = rawdata[46:50]
# delay & reverb config
if rawdata[72] == 0:
    # off
    newdata[99] = 0
    newdata[105] = 0
elif rawdata[62] == 1:
    # delay
    newdata[99] = 1
    newdata[105] = 0
    newdata[100] = rawdata[68]
    newdata[101:103] = rawdata[63:65]
    newdata[103:105] = rawdata[65:67]
    val = int.from_bytes(rawdata[57:59], byteorder='little') - 1
    if val > 0:
        newdata[151:153] = int.to_bytes(val, 2, byteorder='little')
elif rawdata[62] == 2:
    # reverb config
    newdata[99] = 0
    newdata[105] = 1
    newdata[106] = rawdata[67] 
    newdata[107:109] = rawdata[63:65]
    newdata[109:111] = rawdata[65:67]
    val = int.from_bytes(rawdata[57:59], byteorder='little') - 1
    if val > 0:
        newdata[153:155] = int.to_bytes(val, 2, byteorder='little')
# pitch bend range
newdata[111] = rawdata[80+79]
newdata[112] = rawdata[80+80]
# joystick assign (+) = wheel, (-) = pedal
val = wheel_param_map[rawdata[80+77] - 2]
if val >= 0:
    newdata[113] = val
    newdata[114] = rawdata[80+115]

if rawdata[62] == 1:
    # delay is on
    if val == 25:
        newdata[113] = 27
    elif val == 26:
        newdata[113] = 28

val = pedal_param_map[rawdata[80+78]]
if val >= 0:
    newdata[115] = val
    # joystick range (-) = max value
    newdata[116] = 200

if rawdata[62] == 1:
    # delay is on
    if val == 25:
        newdata[115] = 27
    elif val == 26:
        newdata[115] = 28

# micro tuning, scale, program tuning
newdata[122] = rawdata[51]
newdata[123] = rawdata[52]
newdata[124] = rawdata[53]
# cutoff velocity, amp velocity
newdata[128] = rawdata[80+53]
newdata[129] = rawdata[37]
# multi octave, routing
newdata[130] = rawdata[80+30]
newdata[131] = rawdata[80+28]
# EG legato, portament mode, portament bpm sync
newdata[132] = rawdata[80+119]
newdata[133] = rawdata[38]
# program level
newdata[135] = rawdata[40]
# vpm params
newdata[136] = rawdata[80+81]
newdata[137] = rawdata[80+83]
newdata[138] = rawdata[80+85]
newdata[139] = rawdata[80+87]
newdata[140] = rawdata[80+88]
newdata[141] = rawdata[80+91]
# user osc param
newdata[142] = rawdata[80+93]
newdata[143] = rawdata[80+95]
newdata[144] = rawdata[80+97]
newdata[145] = rawdata[80+99]
newdata[146] = rawdata[80+101]
newdata[147] = rawdata[80+103]
newdata[148] = rawdata[80+105]
newdata[149] = rawdata[80+106]
# transpose
newdata[150] = rawdata[54]
# transpose
newdata[150] = rawdata[54]
# tempo
newdata[164:166] = rawdata[24:26]

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
    tmpzip = "mnlgxdprog.zip"
    progfile = zipfile.ZipFile(tmpzip, "w")
    progfile.write('FileInformation.xml')
    progfile.write('Prog_000.prog_info')
    progfile.write('Prog_000.prog_bin')
    progfile.close()
    shutil.copyfile(tmpzip, converted)
    os.chdir(cwd)
