#!/nmr/programs/python/bin/python2.5
"""
renumberProtFile.py reads a prot file from XEASY and changes the spin numbers
in the first column so that it can be imported into CARA without overwriting
existing spins. The user must supply a starting spin ID number, and all other
spins will be numbered from there, in no particular order. 
"""

import sys
sys.path.append('/nmr/programs/python/')
import string

def main():
    if len(sys.argv) != 4:
        print '=============================================================================='
        print 'renumberProtFile.py reads a prot file from XEASY and changes the spin numbers'
        print 'in the first column so that it can be imported into CARA without overwriting'
        print 'existing spins. The user must supply a starting spin ID number, and all other'
        print 'spins will be numbered from there, in no particular order.'
        print ''
        print 'Usage: renumberProtFile.py infile.prot outfile.prot startIndex'
        print 'Number of arguments given: %d'%(len(sys.argv)-1)
        print '=============================================================================='
        return

    infile = sys.argv[1]
    outfile = sys.argv[2]

    if infile == outfile:
        print '\nPlease do not overwrite your original file. Try again.\n'
        return

    startIndex = int(sys.argv[3])

    if startIndex <= 9999:
        numDigits = 6
    else:
        numDigits = len(sys.argv[3]) + 2

    openfile = open(infile)
    lines = openfile.readlines()
    openfile.close()

# How many characters do we need to reserve for the spin IDs?

    numSpins = len(lines)
    maxSpin = startIndex + numSpins
    numChars = len('%d'%maxSpin)
    print maxSpin, numChars
    outputfile = open(outfile,'w')
    spinIDnum = startIndex - 1
    for line in lines:
        spinIDnum = spinIDnum + 1
        spinIDstr = str(spinIDnum).rjust(numDigits)
        fields = line.split()
        atomType = fields[3].ljust(5)
        resNum = fields[4]
        chemShift = float(fields[1])
        newline = '%s %7.3f %s %s %s\n'%(spinIDstr,chemShift,fields[2],atomType,resNum) 
        outputfile.write(newline)
    outputfile.close()

main()
