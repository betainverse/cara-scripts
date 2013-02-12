#!/nmr/programs/python/bin/python2.5
"""
add10000toSpinIDsWithPairs.py takes a cara repository file and renumbers the 
spectrum IDs by adding 10000 to each ID.
Spin IDs are also renumbered in pairs, aka NOEs.

Note that add10000toSpinIDswithPairs.py only alters the first project in a repository, and does not alter tags in peaklists.
"""
import sys
sys.path.append('/nmr/programs/python/')
import xml.etree.ElementTree as ET

# Main
    
def main():
    if len(sys.argv) not in [3,4]:
        print '=============================================================================='
        print 'add1000toSpinIDsWithPairs.py renumbers the spin IDs in a cara'
        print 'repository by adding 10000 to each ID.'
        print 'Spin IDs are also renumbered in spin pairs, aka NOEs.'
        print ''
        print 'Note that add10000toSpinIDsWithPairs.py only alters the first project in a'
        print 'repository by default.'
        print ''
        print 'Usage: add10000toSpinIDsWithPairs.py infile.cara outfile.cara'
        print 'Number of arguments given: %d'%(len(sys.argv)-1)
        print 'An optional third argument (integer) indicates which project to modify, if'
        print 'there is more than one project in a repository. '
        print '=============================================================================='
        return

    infile = sys.argv[1]
    outfile = sys.argv[2]

    if infile == outfile:
        print '\nPlease do not overwrite your original file. Try again.\n'
        return

    tree = ET.parse(infile)
    root = tree.getroot()

# Select a project, the first one by default.

    if len(sys.argv) == 4:
        numProject = int(sys.argv[3])-1
        if numProject < 0:
            print '\nYou requested a negative project number. Try again.\n'
            return
    else:
        numProject = 0

    projects = root.findall('project')
    try:
        project = projects[numProject]
        print 'Modifying project #%d, %s.'%(numProject + 1,project.get('name'))
    except:
        print '\nYou requested project number %d, but there are only %d projects in this repository. Try again.\n'%(numProject + 1, len(projects))
        return



# Find all spins and fix IDs

    spinbase = project.find('spinbase')
    spins = spinbase.findall('spin')
    print 'There are %d total spins.'%len(spins)
    for spin in spins:
        origID = int(spin.get('id'))
        newID = origID + 10000
        spin.set('id','%d'%newID)        

# Find all pairs and fix spin IDs

    pairs = spinbase.findall('pair')
    print 'There are %d total pairs.'%len(pairs)
    for pair in pairs:
        lhs = pair.get('lhs')
        newLHS = int(lhs) + 10000
        pair.set('lhs','%d'%newLHS)
        rhs = pair.get('rhs')
        newRHS = int(rhs) + 10000
        pair.set('rhs','%d'%newRHS)
    
    tree.write(outfile)    

main()

# Testing:

#print 'HEAT-2: %d'%locateStartOfUnassignedResidues(1219,1437,219)
#print '4afl: %d'%locateStartOfUnassignedResidues(1,500,719)
#print 'weird: %d'%locateStartOfUnassignedResidues(500,1050,719)
