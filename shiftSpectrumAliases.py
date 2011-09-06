#!/nmr/programs/python/bin/python2.5
"""
shiftSpectrumAliases.py takes a CARA repository file and alters the
chemical shift of all spin aliases in the indicated spectrum (-s) and
with the indicated tag (-t) by the amount specified (-d). 
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
### Parsing command-line options ##########################################
    # The OptionParser has two purposes here:
    # 1. facilitate obtaining filenames for input and output, and possibly
    #    the name of a project, in case there is more than one project in
    #    the repository
    # 2. provide help text in case the user needs to be reminded of how to
    #    invoke the script. The help text will be printed if the user
    #    invokes the script with the -h or --help option, or if the user
    #    fails to supply an input file. The help file shows the usage, then
    #    then the description, then describes the possible options, and ends
    #    with the epilog.
    # 
    # First we fill in usage, description, and epilog with the text we want
    # to show up in help. Then we define the options, including help text,
    # but also variable names for storing the input and output filenames.
    
    parser = OptionParser() # creates an instance of the parser
    parser.usage = "%prog -i input.cara -d shiftChange -t tag -s spectrumID [-o output.cara] [-p project-name]"
    parser.description = "%prog takes a cara repository file and shifts all the spin aliases with the indicated tag in the indicated spectrum by a specified amount."
    parser.epilog = ""
    parser.add_option("-d", "--shift", dest="shiftChange", type="float",
                      help="Desired change in chemical shift in ppm, required.")
    #parser.add_option("-a", "--aliases", dest="alias", action="store_true", default=False,
    #                  help="Use this flag to change aliases as well as regular spins.")
    parser.add_option("-i", "--input", dest="infile",type="string",default=None,
                      help="name of original CARA repository, required.", metavar="FILE")
    parser.add_option("-o", "--output", dest="outfile",type="string",default=None,
                      help="name of new CARA repository, defaults to stdout.", metavar="FILE")
    parser.add_option("-p", "--project", metavar="NAME", dest="project", default=None,type="string",
                      help="name of project to alter, if there is more than one project in the repository, defaults to the first project.")
    parser.add_option("-t", "--tag", metavar="TAG", dest="tagToShift", default=None,type="string",
                      help="tag of spins to shift, eg N. Required.")
    parser.add_option("-s", "--spectrum",metavar="SPECID",dest="specID",default=None,type="int",
                      help="ID of spectrum with aliases to shift")
    # Now parse the command-line options
    (options, args) = parser.parse_args()

    infile = options.infile
    outfile = options.outfile
    projectName = options.project
    shiftChange = options.shiftChange
    #alias = options.alias
    tagToShift = options.tagToShift
    specIDtoShift = str(options.specID)
    
    if tagToShift == None:
        parser.print_help()
        parser.error("Please specify an atom type tag to shift, such as \"N\".")
    
    if shiftChange == None:
        parser.print_help()
        parser.error("Please specify a chemical shift change in ppm.")

    if infile == None:
        parser.print_help()
        parser.error("Please specify an input file.")

    if outfile == None:
        outfile = stdout
    elif exists(outfile):
        print '\nOutput file \'%s\' exists. Choose a new name to avoid overwriting.\n'%outfile
        return

    alias = False
    if specIDtoShift == None:
        print '\nNo spectrum ID was indicated. All spins will be shifted.\n'
        parser.print_help()
        specIDtoShift = 0
        alias = True

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

# Convert spins

    spinbase = project.find('spinbase')
    spins = spinbase.findall('spin')
    for spin in spins:
        tag = spin.get('tag')
        if tag == tagToShift:
            positions = spin.findall('pos')
            for pos in positions:
                spec = pos.get('spec')
                shift = float(pos.get('shift'))
                if spec == specIDtoShift or alias==True:
                    newshift = str(shift+shiftChange)
                    pos.set('shift',newshift)
                
# Write out the modified xml tree

    tree.write(outfile)

# Execute everything
main()

