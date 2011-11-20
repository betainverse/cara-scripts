#!/nmr/programs/python/bin/python2.5
"""
showSpinLinks.py reads in a CARA repository, and generates a new one in which
spinlinks contain only two spinIDs and no other information about visibility
in particular spectra, etc.

Use showSpinLinks.py -h or showSpinLinks.py --help to learn more about inputs.
"""

### Import some libraries #################################################

from optparse import OptionParser # for parsing commandline input
from sys import stdout # for output to screen instead of to file
import xml.etree.ElementTree as ET # for parsing XML
from os.path import exists # for making sure not to overwrite files

### Data Definitions ######################################################


# spinlink is an xml element representing an NOE from a CARA spinlink
#   Here is a typical xml representation of a spinlink that is visible only
#   in spectrum 176:
#   <pair lhs='37' rhs='1979'>
#   <inst spec='0' rate='0.000000' code='0' visi='0'/>
#   <inst spec='176' rate='0.000000' code='0' visi='1'/>
#   </pair>

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
    parser.usage = "%prog -i input.cara [-o output.cara] [-p project-name]"
    parser.description = "%prog  reads in a CARA repository and removes all characteristics of any spinlinks beyond two spinIDs."
    parser.epilog = ""
    parser.add_option("-i", "--input", dest="infile",type="string",default=None,
                      help="name of original CARA repository, required.", metavar="FILE")
    parser.add_option("-o", "--output", dest="outfile",type="string",default=None,
                      help="name of new CARA repository, defaults to stdout.", metavar="FILE")
    parser.add_option("-p", "--project", metavar="NAME", dest="project", default=None,type="string",
                      help="name of project to alter, if there is more than one project in the repository, defaults to the first project.")

    # Now parse the command-line options
    (options, args) = parser.parse_args()

    infile = options.infile
    outfile = options.outfile
    projectName = options.project

    if infile == None:
        parser.print_help()
        parser.error("Please specify an input cara file.")

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

### Retrieve data from CARA repository ####################################

    spinbase = project.find('spinbase')
    spinlinks = spinbase.findall('pair')

### Iterate through spinlinks #############################################

    for spinlink in spinlinks:
        lhs = spinlink.get('lhs')
        rhs = spinlink.get('rhs')
        spinlink.clear()
        spinlink.attrib['lhs'] = lhs
        spinlink.attrib['rhs'] = rhs

    tree.write(outfile)

#    for string in printstrings:
#        print string

main()
