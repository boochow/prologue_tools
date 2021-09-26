# Korg prologue tools

## prlg2mnlgxd, mnlgxd2prlg

These tools convert a Prologue's patch file (`*.prlgprog`) to Minilogue xd's (`*.mnlgxdprog`) and vice versa.

Usage:

``
 prlg2mnlgxd [-n] [--osc N] filename.prlgprog
``
 
`prlog2mnlgxd` reads a Prologue program file `filename.prlgprog`, then translate it for minilogue XD and writes the program file for minilogue xd "`filename.mnlgxdprog`" into the same directory as the input file. When `-n` is specified, nothing will be written while all conversion warnings are still printed.

When `--osc N` is specified,  the user oscillator slot number is forced to be N.

Example:

```
$ python3 ./prlg2mnlgxd.py 240_Fly-by.prlgprog 
Export to: 240_Fly-by.mnlgxdprog
Info:	Fly-by	UNISON	SAW	SQR	VPM
Warning: Sub timbre is ON, but only main timber is converted
Warning: EG sustain level is high(594), decay time set to maximum value
Warning: EG is used for pitch mod(255), cutoff mod(-93) is ignored
Warning: Fast LFO mode is used but not supported
```

`mnlgxd2prlg` converts a Minilogue XD patch file into a Prologue patch file in the same manner.

## proginfo
This tool shows the value of specified field  in the given program file. See Table 3 of [Prologue's MIDI implementation documnt](https://www.korg.com/us/support/download/manual/0/778/4066/) for details of the program file's data structure.

Usage:

``
 proginfo [-h] [-p] -i] [--offset N[,N2,N3,..]] filename.prlgprog
``

`-h` : show help

`-p` : omit program name

`-i` : omit basic program information

`--offset N` : show the value of the Nth byte
in the program data

You can specify the output format of the value by adding single character after the offset value.

`N` : 8 bit integer

`Nd` : 16 bit integer, little endian

`Nx` : 8 bit integer in hex

`Nc` : character

`Ns` : string, up to 12 characters (for the program name field)

Example:

```
./proginfo.py -i --offset=90,91,92d,94d,118d Runner_Brass.prlgprog 
Runner Brass	2	0	512	0	862
```
offset 90: VCO1 wave (0 : SQR, 1 : TRI, 2 : SAW)

offset 91: VCO1 octave

offset 92-93: VCO1 pitch

offset 94-95: VCO1 shape

offset 118-119: VCO1 level

## setunitnum
This tool changes the slot number of user OSC, user modulation, user delay, or user reverb.

Usage:

``
setunitnum.py [-h] [--osc OSC_NUM] [--mod MOD_NUM] [--delay DELAY_NUM] [--reverb REVERB_NUM] filename.extension
``

A new program file with the given unit numbers will be written into the same directory as `filename`.

The filename will be `filename_O`*OSC_NUM*`_M`*MOD_NUM*`_D`*DELAY_NUM*`_R`*REVERB_NUM*`.extension`.
