# Korg prologue tools

## prlg2mnlgxd

This tool converts a Prologue's patch file (`*.prlgprog`) to Minilogue xd's (`*.mnlgxdprog`).

Usage:

``
 prlg2mnlgxd [--osc N] filename.prlgprog
``
 
This writes the program file for minilogue xd "`file.mnlgxdprog`" into the same directory as the input file.

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