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

Experimental installer. Used when you want to be able to install in two different
ways. For example when trying out an upgraded module.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-10-26
'''
from installer import installer

##
# Decides what installer that should be used depending on python version
#
class pychoiceinstaller(installer):
  ## Constructor
  # @param releasecandidate - the ordinary installer
  # @param experimentalcandidate - the experimental installer
  #
  def __init__(self, py27installer, python3installer):
    super(pychoiceinstaller, self).__init__(py27installer, None)
    self._py27installer = py27installer
    self._py3installer= python3installer
    self._current = self._py27installer
  
  ##
  # Performs the actual installation sequence. Depending on if the software is running
  # in experimental mode or not, different installers will be executed
  # @param env: the build environment
  # @raise InstallerException: if any problem occurs during installation
  # 
  def doinstall(self, env):
    return self._current.doinstall(env)
  
  ##
  # Returns the package that this installer will install
  # @return: the package
  #
  def package(self):
    return self._current.package()

  ##
  # Returns the os environment
  # @return the os environment
  def osenvironment(self):
    return self._current.osenvironment()

  ##
  # Executes the packages fetch_offline_content
  # @param env: the build environment
  #  
  def fetch_offline_content(self, env=None):
    self._py27installer.fetch_offline_content(env)
    self._py3installer.fetch_offline_content(env)

  ##
  # Executes the package cleanup
  # @param env: the build environment
  #
  def clean(self, env=None):
    self._py27installer.clean(env)
    self._py3installer.clean(env)

  ## Sets if we should enable py3 support or not
  # @param usepy3: if py3 should be enabled or not
  #
  def enablePython3(self, usepy3):
    if usepy3 == True:
      self._current = self._py3installer
    else:
      self._current = self._py27installer
