-- Script to shift the ppm of selected spins and their aliases by a fixed amount
-- F. Damberger 22. Feb.2005
-- modified by K. Edmonds 22 June 2011

-- WARNING: always back-up your repository before executing script!
-- Undo by repeating the script with oppposite sign for Delta

-- Below are the User defineable variables. READ points 4 & 5 carefully!
-- -------------------------------------------------------------------------------------------
-- 1. The Project you want to modify shifts in:
         ProjectName = "projectname"

-- 2. Atom Type of spins whose shifts are changed:
         AtomType = "H"

-- 3. Amount to shift the ppm value of spin: newPpm = oldPpm + Shift
         Delta = 0.05

-- 4. Label of spins whose shifts are (NOT) changed:
         Label = "H"

-- 5. Filter for INCLUDE or EXCEPT
--      If the NOT is defined, only spins which do NOT have the label are shifted.
--      If the NOT definition is commented out, only spins which DO have the label are shifted.
--        Filter = "NOT"
-- ---------------------------------------------------------------------------------------------

-- get Project

if cara:getProject( ProjectName ) then
	Project = cara:getProject( ProjectName )
else
	error( "\nERROR: You must edit the header of the script\n to define a valid ProjectName." )
end
-- get Spins into table
SpinsTable = Project:getSpins()

-- go through all spins in table and shift by amount Delta if they are incl. by filter

Spectra = Project:getSpectra()

local i = 0
for SpinId,Spin in pairs( SpinsTable ) do
	if Spin:getAtomType() == AtomType then
	-- Atom type matches
		if Filter == "NOT" then
			-- use NOT filter
			if not ( Spin:getLabel() == Label ) then
				-- shift the spin
				Project:setShift( Spin, Spin:getShift() + Delta )
				i = i + 1 -- keep count of spins shifted
				Shifts = Spin:getShifts()
				for SpecId,Shift in pairs( Shifts ) do -- check all spectra for alias
					Spectrum = Project:getSpectrum( SpecId )
					Project:setShift( Spin, Spin:getShift( Spectrum ) + Delta, Spectrum ) -- then shift it
				end -- for all Shift aliases
			else
				-- does not match filter
			end -- label match
		else
			-- use filter without NOT
			if ( Spin:getLabel() == Label ) then
				-- shift the spin
				-- Project:setShift( Spin, Spin:getShift() + Delta )
				i = i + 1
				Shifts = Spin:getShifts()
				for SpecId,Shift in pairs( Shifts ) do -- check all spectra for alias
					Spectrum = Project:getSpectrum( SpecId )
					Project:setShift( Spin, Spin:getShift( Spectrum ) + Delta, Spectrum ) -- then shift it
				end -- for all shift aliases
			else
				-- does not match filter
			end -- if label matches
		end -- if Filter == "NOT"
	else
         -- wrong atom type
	end -- if AtomType matches
end -- for all spins

print( "shifted the position of "..i.." spins." )
print( "ShiftSpinsAndAliases.lua is done" )
