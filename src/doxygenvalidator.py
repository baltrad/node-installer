'''
Copyright (C) 2012 Swedish Meteorological and Hydrological Institute, SMHI,

This file is part of baltrad node installer.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this software.  If not, see <http://www.gnu.org/licenses/>.
------------------------------------------------------------------------*/

Validates that we have a doxygen generator available

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2012-01-12
'''
import subprocess

##
# Doxygen Validator, tests for an existing doxygen
#
class doxygenvalidator:
  ##
  # Default constructor
  def __init__(self):
    pass
    
  ##
  # Performs the check for a doxygen command
  # @param env: the build environment
  #
  def validate(self, env):
    ocode = subprocess.call("which doxygen > /dev/null 2>&1", shell=True)
    if ocode != 0:
      print "Doxygen: Not found"
    else:
      print "Doxygen: Found"
