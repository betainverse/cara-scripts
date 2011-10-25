#!/nmr/programs/python/bin/python2.5
"""
AddSpinLinksFromUpls.py reads in a CARA repository and a UPL list, and generates spin links in the repository based on the UPL list.

Use AddSpinLinksFromUpls.py -h or AddSpinLinksFromUpls.py --help to learn more about inputs.

WARNING: This script ABSOLUTELY REQUIRES that your system numbers match
your residue numbers. You must first use the script:
NumberCaraSystemsByAssignment.py
"""

### Import some libraries #################################################

from optparse import OptionParser # for parsing commandline input
from sys import stdout # for output to screen instead of to file
import xml.etree.ElementTree as ET # for parsing XML
from os.path import exists # for making sure not to overwrite files

### Helper functions ######################################################

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
    parser.usage = "%prog -i input.cara -u uplfile.upl [-o output.cara] [-p project-name]"
    parser.description = "%prog  reads in a CARA repository and a UPL list, and generates spin links in the repository based on the UPL list."
    parser.epilog = ""
    parser.add_option("-i", "--input", dest="infile",type="string",default=None,
                      help="name of original CARA repository, required.", metavar="FILE")
    parser.add_option("-o", "--output", dest="outfile",type="string",default=None,
                      help="name of new CARA repository, defaults to stdout.", metavar="FILE")
    parser.add_option("-p", "--project", metavar="NAME", dest="project", default=None,type="string",
                      help="name of project to alter, if there is more than one project in the repository, defaults to the first project.")
    parser.add_option("-u", "--upl", dest="uplfile",type="string",default=None,
                      help="name of upl file, required.", metavar="FILE")

    # Now parse the command-line options
    (options, args) = parser.parse_args()

    infile = options.infile
    outfile = options.outfile
    projectName = options.project
    uplfile = options.uplfile

    if infile == None:
        parser.print_help()
        parser.error("Please specify an input cara file.")

    if uplfile == None:
        parser.print_help()
        parser.error("Please specify an input upl file.")
    
    if outfile == None:
        outfile = stdout
    elif exists(outfile):
        print '\nOutput file \'%s\' exists. Choose a new name to avoid overwriting.\n'%outfile
        return
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

    spinbase = project.find('spinbase')
    spins = spinbase.findall('spin')
    pairs = spinbase.findall('pair')
    spindict = {}
    getSpinID = {}
    pairList = []

    for spin in spins:
        atom = spin.get('atom')
        offset = spin.get('off')
        if atom == 'H1':
            spinid = spin.get('id')
            try:
                system = int(spin.get('sys'))
                tag = spin.get('tag')
                spindict[spinid] = {'tag': tag, 'sys': system}
                getSpinID[(system,tag)]=spinid
            except Exception, e:
                print "Orphan spin: ",e

    # Lists of pairs:

    for pair in pairs:
        lhs = pair.get('lhs')
        rhs = pair.get('rhs')
        if int(lhs) < int(rhs):
            pairList.append((lhs,rhs))
        else:
            pairList.append((rhs,lhs))

    # Read UPLs

    openfile= open(uplfile,'r')
    upllines = openfile.readlines()
    openfile.close()

    for line in upllines:
        if line[0] != '#':
            try:
                columns = line.split()
                leftsys = int(columns[0])
                lefttag = columns[2]
                rightsys = int(columns[3])
                righttag = columns[5]
                if leftsys != rightsys:
                    lhs = getSpinID[(leftsys,lefttag)]
                    rhs = getSpinID[(rightsys,righttag)]
                    if int(lhs) < int(rhs) and (lhs,rhs) not in pairList:
                        newpair = ET.Element("pair")
                        newpair.attrib['lhs']=lhs
                        newpair.attrib['rhs']=rhs
                        pairList.append((lhs,rhs))
                        spinbase.append(newpair)
                        #spinbase.append(Element("pair",'lhs'=lhs,'rhs'=rhs)
                    elif int(rhs) < int(lhs) and (rhs,lhs) not in pairList:
                        newpair = ET.Element("pair")
                        newpair.attrib['lhs']=rhs
                        newpair.attrib['rhs']=lhs
                        spinbase.append(newpair)
                        #spinbase.append(Element("pair",'lhs'=rhs,'rhs'=lhs))
                        pairList.append((rhs,lhs))
            except Exception, e:
                print "Bad upl line: ",line           


    tree.write(outfile)

#    for string in printstrings:
#        print string

main()
