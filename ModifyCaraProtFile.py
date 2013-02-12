#!/nmr/programs/python/bin/python2.5
"""
ModifyCaraProtFile.py reads a prot file exported from CARA and adds calibration
values to the H and N chemical shift fields.
"""
import sys
sys.path.append('/nmr/programs/python/')
import string

def main():
    if len(sys.argv) != 5:
        print '=============================================================================='
        print 'ModifyCaraProtFile.py reads a prot file exported from CARA and adds a'
        print 'calibration factor to the H and N chemical shift fields.'
        print ''
        print 'Usage: ModifyCaraProtFile.py infile.prot outfile.prot H N'
        print 'Where H and N are values to be added to each chemical shift for H and N,'
        print 'respectively, eg. ModifyCaraProtFile.py in.prot out.prot -0.141 0.882'
        print 'Number of arguments given: %d'%(len(sys.argv)-1)
        print '=============================================================================='
        return

    infile = sys.argv[1]
    outfile = sys.argv[2]
    Hadjust = float(sys.argv[3])
    Nadjust = float(sys.argv[4])

    if infile == outfile:
        print '\nPlease do not overwrite your original file. Try again.\n'
        return

    openfile = open(infile)
    lines = openfile.readlines()
    openfile.close()
    outputfile = open(outfile,'w')
    for line in lines:
        fields = line.split()
        oldChemShift = float(fields[1])
        atomType = fields[3]
        if atomType == 'H' or atomType == 'HN':
            newChemShift = oldChemShift + Hadjust
        elif atomType == 'N':
            newChemShift = oldChemShift + Nadjust
        else:
            newChemShift = oldChemShift
        newline = fields[0] + ' ' + '%7.3f'%newChemShift + ' '+ fields[2] + ' ' + fields[3].ljust(5) + ' ' + fields[4] + '\n'
        outputfile.write(newline)
    outputfile.close()

main()
