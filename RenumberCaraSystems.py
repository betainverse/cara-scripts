#!/nmr/programs/python/bin/python2.5

"""
RenumberCaraSystems.py takes a cara repository file and renumbers the spin systems so they
run in order with no gaps. By default, the spin system numbers start with 1.
Future plans may include an option to start at another number.

Note that RenumberCaraSystems.py only alters the first project in a repository, and does not alter tags in peaklists.
"""
import sys
sys.path.append('/nmr/programs/python/')
import xml.etree.ElementTree as ET

def main():
    if len(sys.argv) != 3:
        print '=============================================================================='
        print 'RenumberCaraSystems.py renumbers the spin systems in a cara repository so that they begin at 1 and there are no gaps.'
        print 'Note that RenumberCaraSystems.py only alters the first project in a repository, and does not alter tags in peaklists.'
        print ''
        print 'Usage: RenumberCaraSystems.py infile.cara outfile.cara'
        print 'Number of arguments given: %d'%(len(sys.argv)-1)
        print '=============================================================================='
        return
    infile = sys.argv[1]
    outfile = sys.argv[2]

    syscounter = 0
    sysdict = {}

    tree = ET.parse(infile)
    root = tree.getroot()

    firstproject = root.find('project')
    spinbase = firstproject.find('spinbase')
    spinsystems = spinbase.findall('spinsys')

    for spinsystem in spinsystems:
        syscounter = syscounter + 1
        oldid = spinsystem.get('id')
        sysdict[oldid] = '%d'%syscounter
        spinsystem.set('id',sysdict[oldid])
    print '%d systems found.'%syscounter

    links = spinbase.findall('link')
    
    for link in links:
        oldpred = link.get('pred')
        oldsucc = link.get('succ')
        link.set('pred',sysdict[oldpred])
        link.set('succ',sysdict[oldsucc])

    spins = spinbase.findall('spin')

    for spin in spins:
        oldsys = spin.get('sys')
        if oldsys:
            spin.set('sys',sysdict[oldsys])
        else:
            print 'Warning: spin %s has no parent system. The parent system was probably deleted.'%spin.get('id')
            print spin.items()
            # note that the offending spin could be removed. 
    tree.write(outfile)

main()
