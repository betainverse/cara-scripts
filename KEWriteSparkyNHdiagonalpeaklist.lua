-- KEWriteSparkyHSQCList.lua
-- Purpose: writes an H-N peaklist for importing into sparky with the command rp
-- written by K.Edmonds 2010, based on 
-- WriteShiftsInColumns.lua written by F.Damberger 11:14 April 4 2006  to 11:40

function Format( Number ) -- function to format the chemical shifts
	FormattedNumber = string.format( "%3.2f", Number )
	return FormattedNumber
end

-- User editable parameters are below: ===========================

-- Spacer between elements of table to write out:
Spacer = " "
Tag = "N-H-H"
-- Table of spin labels whose shifts should be written to a column

SpinsInColumns = {}
SpinsInColumns[ 1 ] = "N"
SpinsInColumns[ 2 ] = "H"
SpinsInColumns[ 3 ] = "H"

-- End of user editable section ==================================
-- define a table of temporary script variables
t={}

-- Get Parameters from User

-- 1. Get Project: ------------------------------------------------
local projectnames = {}
i=0
for ProjName,Proj in pairs( cara:getProjects() ) do
	i = i + 1
	projectnames[ i ] = ProjName
end

if i==1 then
	t.ProjectName = projectnames[ i ]
else
	t.ProjectName = dlg.getSymbol( "Choose project", "select one", unpack( projectnames ) )
end
if not t.ProjectName then
	error( "No project name defined")
else
	t.P = cara:getProject( t.ProjectName )
end

-- 2. Get Output filename: -----------------------------------------
t.FileName = dlg.getText( "Enter output filename", "output filename","HNpeaklist.list" )

--3. Get Label of Spin to write out chemical shifts from
-- I replaced this step with a table , see the top of the script
--t.Label = dlg.getText( "Enter label of the spins whose chemical shifts you want to write out : ", "Enter Label of spins whose shifts will be written out (e.g. HA): ")


-- loop through the sequence and for each residue, create a Line
-- then for each Line look for each column entry in turn
-- add it to the end of the growing line

Seq = t.P:getSequence()
j = 0
Lines = {}
for ResId,Res in pairs( Seq ) do
	Sys = Res:getSystem()
	AA = Res:getType():getLetter()
	if Sys then -- if residue is assigned
		SpinsInSys = Sys:getSpins()
		j = j + 1
		Lines[ j ] = AA..ResId..Tag
		for k = 1,table.getn( SpinsInColumns ) do
			LabelToFind = SpinsInColumns[ k ]
			MatchingSpin = nil -- reset to none found
			for SpinId,Spin in pairs( SpinsInSys ) do -- search for a match to LabelToFind
				if Spin:getLabel() == LabelToFind then
					MatchingSpin = Spin
				end -- if Spins label matches LabelToFind
			end -- for all Spins in System (look for match to this Label)
			if MatchingSpin then
				FormShift = Format( MatchingSpin:getShift() )
				Lines[ j ] = Lines[ j ]..Spacer..FormShift
			else
				Lines[ j ] = Lines[ j ]..Spacer -- no shift assigned, leave empty
			end
		end -- for all elements k of SpinsInColumns (try to find a shift for this label)
		--Lines[ j ] = Lines[ j ].."\n" -- next line
	end -- if System is assigned
end -- for all residues in sequence

--create string "Table" with lines

--create the first line of table
for m = 1,table.getn( SpinsInColumns ) do
	if m == 1 then
		Labels = SpinsInColumns[ 1 ]
	else
		Labels = Labels..Spacer..SpinsInColumns[ m ]
	end
end
Header = "Residue"..Spacer..Labels

for l=1,table.getn( Lines ) do
	if l==1 then
		Table = Header.."\n"..Lines[ l ]
	else
		Table = Table.."\n"..Lines[ l ]
	end
end

-- Now write out all lines to a file
file = io.open( t.FileName, "w" )
file:write( Table )
file:flush()
file:close()
print("Wrote out "..table.getn( Lines ).." lines to file "..t.FileName )
print( "script WriteShiftsInColumns is done" )
t = nil


