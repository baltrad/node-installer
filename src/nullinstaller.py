'''
Copyright (C) 2011 Swedish Meteorological and Hydrological Institute, SMHI,

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

Null installer that does nothing

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2016-09-27
'''

from installer import installer

##
# The null installer
#
class nullinstaller(installer):
  ##
  # Constructor
  # Installs the beast package. 
  #
  def __init__(self, pkg):
    super(nullinstaller, self).__init__(pkg)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    pass
  