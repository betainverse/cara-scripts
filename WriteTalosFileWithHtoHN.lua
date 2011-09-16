--WriteTalosFile.lua
--Version 1
--8-06-07
--Andrew Severin
--severin at iastate dot edu
-- 2010-08-15 Rochus Keller:
-- some minor corrections
--Version 2
-- F.Damberger
-- modified to introduce a menu dialog for entering user preferences
-- simplified the script and adjusted for correct talos output file format
--Version 3
-- K. Edmonds 16 September 2011
-- modified to separate C' from CA/CB referencing
-- fixed export of amide proton chemical shifts
-- fixed bug in sequence output

--This script converts information in the repository to a Talos input script.
--be sure to modify the inputs to your particular protein.  If your spectra are already calibrated to a standard then
--make the t.cal. variables all zero.

--Create Object Table for Script

t={}
--inputs -- MUST BE EDITED BY USER ----------------------------------------------

-- PLEASE run $ talos+ -in input.tab -check 
-- in order to check whether your referencing went in the right direction!!

FileSuffix = "tab"
TableOfMatchingLabels = { "HN","H", "N", "HA", "HA2", "HA3", "C", "CA", "CB" }
t.cal={}          --The next four lines should be updated if you need 
t.cal.C=0.000     --to calibrate the output of your shifts according 
t.cal.HA=0.000        --to a standard (ie DSS)

t.cal.CA=0.000     -- alternatively, you can use the scripts ShiftSpinsInCatagory.lua and RecalibrateSpectra.lua to adjust spin shifts & spectra to a DSS calibration 
t.cal.CB=0.000
t.cal.H=0
t.cal.HN=t.cal.H
t.cal.N=0
t.cal.HA2=t.cal.HA
t.cal.HA3=t.cal.HA
--end of user inputs -- ----------------------------------------------

function Form( Format, Input )
	return string.format( Format, Input )
end

function GetTalosLine( Index, Spin )
	FormResId = Form("%4d", Index )
	FormResLett = Spin:getSystem():getResidue():getType():getLetter()
	if Spin:getLabel() == "H" then
		FormLabel = Form( "%4s","HN" )
	else
		FormLabel = Form( "%4s",Spin:getLabel() )
	end
	FormShift = Form( "%8.3f", Spin:getShift()+t.cal[ Spin:getLabel() ] )
	return FormResId.." "..FormResLett.."     "..FormLabel.."     "..FormShift
end

function MatchingLabel( Spin )
	for Index,LabelInTable in pairs( TableOfMatchingLabels ) do
		if Spin:getLabel() == LabelInTable then
			return true
		end
	end
	return false
end
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
	t.Project = cara:getProject( t.ProjectName )
end

-- 2. Get Output filename: -----------------------------------------
t.filename = dlg.getText( "Enter output filename for TALOS", "output filename",t.ProjectName.."_talos."..FileSuffix )

-- get lowest and highest sequence Id
t.seq=t.Project:getSequence()
for Id,Res in pairs(t.seq) do
   if not t.seqstart then t.seqstart = Id end
   if not t.seqend then t.seqend = Id end
   if Id < t.seqstart then t.seqstart = Id end
   if Id > t.seqend then t.seqend = Id end
end
-- table.sort(t.seq) -- RK: this seems to be unnecessary and reason for crash
t.file=io.open( t.filename, "w" )
t.singleletter=''
for i=t.seqstart,t.seqend do
	t.singleletter = t.singleletter..t.Project:getResidue(i):getType():getLetter()
end
print("DATA SEQUENCE "..t.singleletter)
t.file:write("DATA SEQUENCE "..t.singleletter.."\n")
print("VARS  RESID RESNAME ATOMNAME SHIFT")
t.file:write("VARS  RESID RESNAME ATOMNAME SHIFT\n")
print("FORMAT %4d %1s     %4s     %8.3f")
t.file:write("FORMAT %4d %1s     %4s     %8.3f\n")
for i=t.seqstart,t.seqend do
	t.sys = t.Project:getResidue(i):getSystem()  
	if t.sys ~= nil then -- RK: this is necessary if not all residues are assigned
		for SpinId,Spin in pairs(t.sys:getSpins()) do
			t.seqat1=i-t.seqstart+1
			if MatchingLabel( Spin ) then
				TalosLine = GetTalosLine( t.seqat1, Spin )
				print(TalosLine)
				t.file:write(TalosLine.."\n")
			end			
		end
	else
		print( "*** Residue "..i.." is not assigned!" )
	end
end





t.file:flush()
t.file:close()
print("wrote talos script file: "..t.filename)
print("WriteTalosFile.lua is finished")
