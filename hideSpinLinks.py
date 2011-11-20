#!/nmr/programs/python/bin/python2.5
"""
showSpinLinks.py reads in a CARA repository, and generates a new one in which
spinlinks meeting certain criteria appear only in the specified spectrum or
spectra.

The user will modify the selection function in the script to describe the
spinlinks of interest. For example, a user might want spinlinks involving
at least one atom with tag 'H' to appear only in spectra that were acquired
on samples in H2O buffer. The user may also specify a list of residue numbers
for which this selection should apply. In this case, that would be a list of
residues with exchangeable amides.

Use showSpinLinks.py -h or showSpinLinks.py --help to learn more about inputs.
"""

### Import some libraries #################################################

from optparse import OptionParser # for parsing commandline input
from sys import stdout # for output to screen instead of to file
import xml.etree.ElementTree as ET # for parsing XML
from os.path import exists # for making sure not to overwrite files

### Data Definitions ######################################################

# spindict is a dict[spinID,attributeDict]
# attributeDict is a dict["tag":atomType, "sys":systemID, "res":residueID, "AA":residueType]
# spinID, systemID, and residueID, and spectrumID are integers
# atomType or tag is a string such as 'H','HA','HA2', etc.
# residueType or AA is a string indicating amino acid, such as 'GLY', 'ALA', etc. 
# spinlink is an xml element representing an NOE from a CARA spinlink
#   Here is a typical xml representation of a spinlink that is visible only
#   in spectrum 176:
#   <pair lhs='37' rhs='1979'>
#   <inst spec='0' rate='0.000000' code='0' visi='0'/>
#   <inst spec='176' rate='0.000000' code='0' visi='1'/>
#   </pair>
# pair is another representation of a spinlink, simply a tuple of two spinIDs.


### Helper functions ######################################################

def hasExchangeableSpin(spindict,spinlink):
    """
    hasExchangeableSpin: spindict, spinlink -> bool
    returns true if a spinlink pair contains an exchangeable spin, 
    so that it should not appear in spectra recorded in D2O.
    """
    lhs = int(spinlink.get('lhs'))
    rhs = int(spinlink.get('rhs'))
    if isExchangeable(spindict,lhs) or isExchangeable(spindict,rhs):
        return True
    else:
        return False

def hasDeuteratedSpin(spindict,spinlink):
    """
    hasDeuteratedSpin: spindict, spinlink -> bool
    returns true if a spinlink pair matches the criteria, so that it should
    only appear in specified spectra.
    """
    lhs = int(spinlink.get('lhs'))
    rhs = int(spinlink.get('rhs'))
    if isDeuterated(spindict,lhs) or isDeuterated(spindict,rhs):
        return True
    else:
        return False

def isExchangeable(spindict,spinID):
    """
    isExchangeable: spindict, spinID -> bool
    returns true if the spin is an exchangeable proton, and
    therefore should not appear in spectra taken in D2O.

    applied awk '($1 ~ 'N-H') {print substr($1,2,4)}' month.list | tr '\n' ','
    to a sparky peaklist from an HSQC in D2O to generate residue lists.
    """
    halfday = [1251,1254,1264,1278,1279,1280,1295,1296,1298,1299,1300,1301,1302,1303,1304,1305,1306,1307,1316,1317,1318,1319,1320,1321,1324,1339,1340,1341,1342,1343,1344,1345,1346,1348,1349,1359,1360,1363,1364,1377,1378,1379,1380,1381,1382,1383,1384,1385,1396,1397,1398,1399]
    month = [1301,1302,1303,1304,1305,1306,1317,1320,1340,1341,1342,1343,1344,1345,1346,1348,1363,1378,1380,1381,1383,1384,1397,1398]
    halfdayOver100000 = [1278,1279,1280,1299,1300,1301,1302,1303,1304,1305,1306,1307,1316,1317,1318,1319,1320,1321,1324,1339,1340,1341,1342,1343,1344,1345,1346,1348,1349,1359,1360,1363,1364,1377,1378,1379,1380,1381,1382,1383,1384,1396,1397,1398,1399]
    residuesWithProtectedAmides = halfdayOver100000
    AA = spindict[spinID]['AA']
    residueID = spindict[spinID]['res']
    atomType = spindict[spinID]['tag']
    if atomType == 'H' and residueID in residuesWithProtectedAmides:
            return False
    elif atomType == 'H':
            return True
    elif AA == 'TRP' and atomType == 'HE1':
        return True
    elif AA == 'THR' and atomType == 'HG1':
        return True
    elif AA == 'HIS' and atomType == 'HD1':
        return True
    elif AA == 'GLN' and (atomType == 'HE21' or atomType == 'HE22'):
        return True
    elif AA == 'ASN' and (atomType == 'HD21' or atomType == 'HD22'):
        return True
    elif AA == 'ARG' and atomType == 'HE':
        return True
    elif AA == 'CYS' and atomType == 'HG':
        return True
    else:
        return False

def isDeuterated(spindict,spinID):
    """
    isDeuterated: spindict, spinID -> bool
    returns true if a spin would be deuterated if the protein is expressed in
    deuterated growth media, and therefore should not appear in certain spectra.
    """
    deuteratedResidues = range(4,10)  # range(4,10) = [4,5,6,7,8,9]
    deuteratedAtomTypes = []
    AA = spindict[spinID]['AA']
    residueID = spindict[spinID]['res']
    atomType = spindict[spinID]['tag']
    if residueID in deuteratedResidues and atomType in deuteratedAtomTypes:
        return True
    else:
        return False

def makeSpinlinkVisible(spinlink,spectrumID):
    """
    makeSpinlinkVisible spinlink,spectrumID -> void
    adds a child to the spinlink element, making it visible in the specified
    spectrum
    """
    child = ET.Element("inst")
    child.attrib["spec"] = str(spectrumID)
    child.attrib["rate"] = '0.000000'
    child.attrib["code"] = '0'
    child.attrib["visi"] = '1'
    spinlink.append(child)

def makeSpinlinkInvisible(spinlink,spectrumID):
    """
    makeSpinlinkVisible spinlink,spectrumID -> void
    adds a child to the spinlink element, making it visible in the specified
    spectrum
    """
    child = ET.Element("inst")
    child.attrib["spec"] = str(spectrumID)
    child.attrib["rate"] = '0.000000'
    child.attrib["code"] = '0'
    child.attrib["visi"] = '0'
    spinlink.append(child)

def printSpinlink(spindict,spinlink):
    """
    printSpinLink spindict, spinlink -> string
    returns a string with a representation of a spinlink for printing to a log file.
    """
    lhs = int(spinlink.get('lhs'))
    rhs = int(spinlink.get('rhs'))
    lAA = spindict[lhs]['AA']
    lresidueID = spindict[lhs]['res']
    latomType = spindict[lhs]['tag']    
    rAA = spindict[rhs]['AA']
    rresidueID = spindict[rhs]['res']
    ratomType = spindict[rhs]['tag']    
    return "%s %s %s\t-\t%s %s %s\n"%(lAA,lresidueID,latomType,rAA,rresidueID,ratomType)

def getProject(projectName,projects):
    """This function, getProject, is only used if the user specifies a project
    name from the command line, rather than simply allowing the script to
    select the first (and likely only) project in a repository."""
    for project in projects:
        if project.get('name') == projectName:
            return project
    # if that doesn't work, raise an error: 
    raise NameError,"There is no project named \"%s\"."%projectName

### Main body of the script ###############################################

def main():
    parser = OptionParser() # creates an instance of the parser
    parser.usage = "%prog -i input.cara [-o output.cara] [-p project-name]"
    parser.description = "%prog  reads in a CARA repository and changes the visibility of specified classes of spinlinks in specified spectra. It is recommended to run showAllSpinLinks.py before running this script."
    parser.epilog = ""
    parser.add_option("-i", "--input", dest="infile",type="string",default=None,
                      help="name of original CARA repository, required.", metavar="FILE")
    parser.add_option("-o", "--output", dest="outfile",type="string",default=None,
                      help="name of new CARA repository, defaults to stdout.", metavar="FILE")
    parser.add_option("-p", "--project", metavar="NAME", dest="project", default=None,type="string",
                      help="name of project to alter, if there is more than one project in the repository, defaults to the first project.")
    parser.add_option("-l","--log",metavar="FILE",dest="log",default=None,type="string",
                      help="name of log file.")

    # Now parse the command-line options
    (options, args) = parser.parse_args()

    infile = options.infile
    outfile = options.outfile
    projectName = options.project
    log = options.log

    if infile == None:
        parser.print_help()
        parser.error("Please specify an input cara file.")

    if outfile == None:
        outfile = stdout
    elif exists(outfile):
        print '\nOutput file \'%s\' exists. Choose a new name to avoid overwriting.\n'%outfile
        return

    if log == None:
        log = stdout
    
    # Now that we have an input file and we know where to send the output, we parse the xml.

    tree = ET.parse(infile)
    root = tree.getroot() #retrieves the whole repository
    projects = root.findall('project') #retrieves every project in the repository

# Select a project according to command-line input, defaulting to the first project

    if projectName:
        project = getProject(projectName,projects)
        if not project:
            print 'No project found with name \"%s\".'%projectName
            return
    else:
        project = projects[0]
        if not project:
            print 'No project found.'
            return

### Retrieve data from CARA repository ####################################

    spinbase = project.find('spinbase')
    spins = spinbase.findall('spin')
    spinlinks = spinbase.findall('pair')
    systems = spinbase.findall('spinsys')
    sequence = project.find('sequence')
    residues = sequence.findall('residue')

### Organize CARA repository data into dictionaries #######################
    
    spindict = {}
    sysdict = {}
    resdict = {}

    for res in residues:
        residueID = int(res.get('id'))
        residueType = res.get('type')
        resdict[residueID] = residueType

    for sys in systems:
        systemID = int(sys.get('id'))
        try:
            residueID = int(sys.get('ass'))
        except Exception, e:
            residueID = None
        sysdict[systemID] = residueID

    for spin in spins:
        atom = spin.get('atom')
        offset = spin.get('off')
        if atom == 'H1':
            spinid = int(spin.get('id'))
            try:
                systemID = int(spin.get('sys'))
                residueID = sysdict[systemID]
                residueType = resdict[residueID]
                tag = spin.get('tag')
                spindict[spinid] = {'tag': tag, 'sys': systemID, 'res': residueID, 'AA':residueType}
            except Exception, e:
                print "Orphan spin: ",e

### Iterate through spinlinks #############################################


    logfile = open(log,'w')
#    spectraH2O = [176]
    spectraD2O = [174,194]

    # make spinlinks generally invisible if they have exchangeable spins,
    # but visible for spectra in H2O

    for spinlink in spinlinks:
        if hasExchangeableSpin(spindict,spinlink):
            logfile.write("Exchangeable: %s"%printSpinlink(spindict,spinlink))
            for spectrumID in spectraD2O:
                makeSpinlinkInvisible(spinlink,spectrumID)

    spectraWdeutTAD = []

    # make spinlinks with deuterated components invisible in particular spectra

    for spinlink in spinlinks:
        if hasDeuteratedSpin(spindict,spinlink):
            logfile.write("Deuterated: %s"%printSpinlink(spindict,spinlink))            
            for spectrumID in spectraWdeutTAD:
                makeSpinlinkInvisible(spinlink,spectrumID)

    logfile.close()
    tree.write(outfile)

#    for string in printstrings:
#        print string

main()
