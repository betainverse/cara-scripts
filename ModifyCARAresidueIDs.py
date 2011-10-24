#!/nmr/programs/python/bin/python2.5
"""
ModifyCARAresidueIDs.py takes a cara repository file and renumbers the residue
ids in the sequence by replacing them with the sequence numbers. Note that this is only
necessary for domains that are not at the N-terminus of the protein.
"""

### Import some libraries #################################################

# OptionParser helps us parse the command line to find input and output file names
from optparse import OptionParser
# If the user doesn't specify an ouput file, we will print the results to stdout,
# so we need to import stdout from the sys module
from sys import stdout

# Import ElementTree for parsing XML
import xml.etree.ElementTree as ET

# This is just for checking to make sure you don't accidentally overwrite files.
from os.path import exists

### Helper functions ######################################################

def makeSequenceDictionary(project):
    """ This function, makeSequenceDictionary, reads the existing sequence to
    create a lookup table (aka dictionary) to convert the old ID to the new
    sequence number.
    As long as we are going through residue list, we will also set the residue
    IDs to the new values."""
    sequence = project.find('sequence')
    residues = sequence.findall('residue')
    sequenceDictionary = {} # create the dictionary
    for residue in residues: # populate the dictionary and fix residue IDs
        realAssignment = residue.get('nr')
        caraAssignment = residue.get('id')
        sequenceDictionary[caraAssignment] = realAssignment # create dictionary entry
        residue.set('id',realAssignment) # change the residue ID
    return sequenceDictionary

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
    parser.usage = "%prog -i input.cara [-o output.cara] [-p project-name]"
    parser.description = "%prog takes a cara repository file and renumbers the residue IDs (which start at 1) in the sequence by replacing them with the sequence numbers. Note that this is only necessary for domains that are not at the N-terminus of the protein."
    parser.epilog = "This script makes it easier to navigate residues of a protein fragment with high residue numbers in CARA. For example, if you are working on a C-terminal domain beginning with residue 220 of the full-length protein, CARA normally wants you to type \"gr 3\" to access residue 222. After running this script, you will be able to access residue 222 with \"gr 222\"."

    parser.add_option("-o", "--output", dest="outfile",type="string",default=None,
                      help="name of new CARA repository, defaults to stdout", metavar="FILE")
    parser.add_option("-i", "--input", dest="infile",type="string",default=None,
                      help="name of original CARA repository, required", metavar="FILE")
    parser.add_option("-p", "--project", metavar="NAME", dest="project", default=None,type="string",
                      help="name of project to alter, if there is more than one project in the repository, defaults to the first project")

    # Now parse the command-line options
    (options, args) = parser.parse_args()
    infile = options.infile
    outfile = options.outfile
    projectName = options.project

    if infile == None:
        parser.print_help()
        parser.error("Please specify an input file.")

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

# Fix residue ids in the sequence

    sequenceDictionary = makeSequenceDictionary(project)



# Convert system assignments

    spinbase = project.find('spinbase')
    spinsystems = spinbase.findall('spinsys')
    for spinsystem in spinsystems:
        oldAssignment = spinsystem.get('ass')
        if oldAssignment:
            newAssignment = sequenceDictionary[oldAssignment]
            spinsystem.set('ass',newAssignment)

# Write out the modified xml tree

    tree.write(outfile)

# Execute everything
main()

