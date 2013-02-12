#!/nmr/programs/python/bin/python2.5
"""
AddUnlabeledSchemeToResidueType.py reads in a cara repository file and modifies
the residue-type definitions to include a labeling scheme with N14 and C12.
A labeling scheme called 'unlabeled' is added for this purpose.
"""

import sys
sys.path.append('/nmr/programs/python/')
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
import string

def main():
    if len(sys.argv) not in [3,4]:
        print '==============================================================================='
        print 'AddILVlabelingScheme.py reads in a cara repository file and modifies the'
        print 'residue-type definitions to include a labeling scheme with 12C and 2H'
        print 'except at methyl groups of I, L, and V.'
        print ''
        print 'A labeling scheme called \'ILVnoesy\' is added for this purpose.'
        print ''
        print 'Usage: AddILVlabelingScheme.py infile.cara outfile.cara'
        print 'Number of arguments given: %d'%(len(sys.argv)-1)
        print 'An optional third argument names which project to modify, if'
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
    projects = root.findall('project')

# Select a project according to command-line input, defaulting to the first project

    if len(sys.argv) == 4:
        projectName = sys.argv[3]
        project = getProject(projectName,projects)
        if not project:
            print 'No project found with name \"%s\".'%projectName
            return
    else:
        project = projects[0]
        if not project:
            print 'No project found.'
            return

# Find existing schemes & make a new one by incrementing the highest existing ID number

    library = root.find('library')
    schemes = library.findall('scheme')
    numSchemes = len(schemes)
    if numSchemes > 0:
        schemeIDs = [int(scheme.get('id')) for scheme in schemes]
        schemeIDs.sort()
        newIDnum = schemeIDs[numSchemes-1]+1
        newID = '%d'%newIDnum
    else:
        newID = '1'
    newscheme = SubElement(library,'scheme')
    newscheme.attrib['id'] = newID
    newscheme.attrib['name'] = 'ILVnoesy15N-%s'%newID

# Modify residue-type

    residueTypes = library.findall('residue-type')
    for residueType in residueTypes:
        if residueType.get('letter') not in ('I','L','V'):
            atoms = residueType.findall('atom')
            for atom in atoms:
                if atom.get('name')[0]=='C':
                    newscheme = SubElement(atom,'scheme')
                    newscheme.attrib['id'] = newID
                    newscheme.attrib['type'] = 'C12'
                elif atom.get('name')[0]=='H' and atom.get('name')!='H':
                    newscheme = SubElement(atom,'scheme')
                    newscheme.attrib['id'] = newID
                    newscheme.attrib['type'] = 'H2'
        elif residueType.get('letter')=='L':
            atoms = residueType.findall('atom')
            for atom in atoms:
                if atom.get('name')[0]=='C' and atom.get('name')[0:2]!='CD':
                    newscheme = SubElement(atom,'scheme')
                    newscheme.attrib['id'] = newID
                    newscheme.attrib['type'] = 'C12'
                elif atom.get('name')[0]=='H' and atom.get('name')[0:2]!='HD' and atom.get('name')!='H':
                    newscheme = SubElement(atom,'scheme')
                    newscheme.attrib['id'] = newID
                    newscheme.attrib['type'] = 'H2'
        elif residueType.get('letter')=='V':
            atoms = residueType.findall('atom')
            for atom in atoms:
                if atom.get('name')[0]=='C' and atom.get('name')[0:2]!='CG':
                    newscheme = SubElement(atom,'scheme')
                    newscheme.attrib['id'] = newID
                    newscheme.attrib['type'] = 'C12'
                elif atom.get('name')[0]=='H' and atom.get('name')[0:2]!='HG' and atom.get('name')!='H':
                    newscheme = SubElement(atom,'scheme')
                    newscheme.attrib['id'] = newID
                    newscheme.attrib['type'] = 'H2'
        elif residueType.get('letter')=='I':
            atoms = residueType.findall('atom')
            for atom in atoms:
                if atom.get('name')[0]=='C' and atom.get('name')[0:2]!='CD':
                    newscheme = SubElement(atom,'scheme')
                    newscheme.attrib['id'] = newID
                    newscheme.attrib['type'] = 'C12'
                elif atom.get('name')[0]=='H' and atom.get('name')[0:2]!='HD' and atom.get('name')!='H':
                    newscheme = SubElement(atom,'scheme')
                    newscheme.attrib['id'] = newID
                    newscheme.attrib['type'] = 'H2'
            
                    
                
    tree.write(outfile)
    
main()
