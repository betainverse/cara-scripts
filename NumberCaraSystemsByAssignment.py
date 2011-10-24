#!/nmr/programs/python/bin/python2.5
"""
NumberCaraSystemsByAssignment.py takes a cara repository file and renumbers the spin systems so they
match their assignment, if they are assigned. Unassigned spin systems are given
numbers that run in order, with no gaps, either starting from 1 or 1001. 
Future plans may include an option to start at another number.

Note that NumberCaraSystemsByAssignment.py only alters the first project in a repository, and does not alter tags in peaklists.
"""
import sys
sys.path.append('/nmr/programs/python/')
import xml.etree.ElementTree as ET

# Functions for determining where to start numbering unassigned systems.

def overlap(start1,end1,start2,end2):
    """Assume for now that start1 < end1 and start2 < end2"""
    if start1 in range(start2,end2+1) or end1 in range(start2,end2+1):
        return True
    if start2 in range(start1,end1+1) or end2 in range(start1,end1+1):
        return True
    else:
        return False

def locateStartOfUnassignedResidues(startAssignment,endAssignment,numSystems):
    if endAssignment < 1000:
        return 1000
    if not overlap(1,numSystems,startAssignment,endAssignment):
        return 0
    end = int(endAssignment)
    return ((end/1000)*1000)+1000

# Main
    
def main():
    if len(sys.argv) not in [3,4]:
        print '=============================================================================='
        print 'NumberCaraSystemsByAssignment.py renumbers the spin systems in a cara'
        print 'repository so that they match their assignment. Unassigned spin systems are'
        print 'given numbers that run in order, starting from 1001 by default.'
        print ''
        print 'Note that NumberCaraSystemsByAssignment.py only alters the first project in a'
        print 'repository by default, and does not alter tags in peaklists.'
        print ''
        print 'Usage: NumberCaraSystemsByAssignment.py infile.cara outfile.cara'
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
    

# Read the sequence and determine the assignments
# Assignments within CARA are considered to start at 1,
# so the sequence information provides a conversion from
# the cara assignment to the real protein sequence.
# sequenceDictionary performs this conversion.

    sequence = project.find('sequence')
    residues = sequence.findall('residue')

    sequenceDictionary = {}

    for residue in residues:
        realAssignment = residue.get('nr')
        caraAssignment = residue.get('id')
        sequenceDictionary[caraAssignment] = realAssignment

    caraAssignments = sequenceDictionary.keys()
    realAssignments = [int(sequenceDictionary[ass]) for ass in caraAssignments]
    realAssignments.sort()
    startAssignment = realAssignments[0]
    endAssignment = realAssignments[len(realAssignments)-1]
    
    print 'Real assignments run from %d to %d.'%(realAssignments[0],realAssignments[len(realAssignments)-1])

# Read & count spin systems

    spinbase = project.find('spinbase')
    spinsystems = spinbase.findall('spinsys')
    numSystems = len(spinsystems)
    
    print 'There are %d total systems.'%len(spinsystems)

# Determine whether to start numbering unassigned systems at 1, 1001,
# or some other number, trying to avoid overlap with assigned systemss.
    
    startUnassignedResidues = locateStartOfUnassignedResidues(startAssignment,endAssignment,numSystems)
    unassignedCounter = startUnassignedResidues
    assignedCounter = 0

    SysIDconverter = {}

    for spinsystem in spinsystems:
        caraAssignment = spinsystem.get('ass')
        oldSysID = spinsystem.get('id')
        if caraAssignment:
            assignedCounter = assignedCounter + 1
            realAssignment = sequenceDictionary[caraAssignment]
            SysIDconverter[oldSysID] = realAssignment
            spinsystem.set('id',SysIDconverter[oldSysID])            
        else:
            unassignedCounter = unassignedCounter + 1
            print 'Unassigned: %d, %s'%(unassignedCounter, spinsystem.items())
            SysIDconverter[oldSysID] = '%d'%unassignedCounter
            spinsystem.set('id',SysIDconverter[oldSysID])

    print 'Found %d assigned systems and %d unassigned systems.'%(assignedCounter, unassignedCounter-startUnassignedResidues)

    links = spinbase.findall('link')

    numlinks = 0

    for link in links:
        numlinks = numlinks + 1
        oldpred = link.get('pred')
        oldsucc = link.get('succ')
        link.set('pred',SysIDconverter[oldpred])
        link.set('succ',SysIDconverter[oldsucc])

    print 'Converted %d system links.'%numlinks

    spins = spinbase.findall('spin')

    numspins = 0

    for spin in spins:
        numspins = numspins + 1
        oldsys = spin.get('sys')
        if oldsys:
            spin.set('sys',SysIDconverter[oldsys])
        else:
            print 'Warning: spin %s has no parent system. The parent system was probably deleted.'%spin.get('id')
            print spin.items()
            # note that the offending spin could be removed.

    print 'Converted %d spins to have the correct parent system.'%numspins
    
    tree.write(outfile)    

main()

# Testing:

#print 'HEAT-2: %d'%locateStartOfUnassignedResidues(1219,1437,219)
#print '4afl: %d'%locateStartOfUnassignedResidues(1,500,719)
#print 'weird: %d'%locateStartOfUnassignedResidues(500,1050,719)
