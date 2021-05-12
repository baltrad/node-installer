'''
Copyright (C) 2018 Swedish Meteorological and Hydrological Institute, SMHI,

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

Rave specific package which is more suitable for defining the handling of rave
packages for now since we have two different variants that are doing the same thing
but resides in two different repositories.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2018-03-31
'''
from package import package
from nodedefinition import NODE_REPOSITORY
from gitfetcher import gitfetcher

##
# The package/module class
#
class rave_package(package):
  
  ##
  # Constructor
  # @param name: the name of the package, e.g. ZLIB
  # @param version: the version of the package, e.g. 1.2.4
  # @param fetcher: a fetcher, that always returns a directory
  # @param depends: if this package depends on any other packages
  #
  def __init__(self, depends=[]):
    rave3ver = NODE_REPOSITORY["RAVE"].getversion()
    rave3uri = NODE_REPOSITORY["RAVE"].geturi()
    rave3branch = NODE_REPOSITORY["RAVE"].getbranch()
    rave3fetcher = gitfetcher(rave3uri, rave3ver, rave3branch)
    self._rave3package=package("RAVE", rave3ver, rave3fetcher, depends)
    self._currentpackage=self._rave3package
    super(rave_package, self).__init__("RAVE", "UNDEFINED")
  
  ##
  # Executes the fetcher. Can both work in offline and online mode
  # @return: a directory where the package can be accessed
  #
  def fetch(self, env=None):
    return self._currentpackage.fetch(env)
  
  ##
  # Executes the cleaner. Can both work in offline and online mode
  #
  def clean(self, env=None):
    self._rave27package.clean(env)
    self._rave3package.clean(env)
  
  ##
  # Fetches the 'offline' content for this package
  # @param env: the build environment
  #  
  def fetch_offline_content(self, env=None):
    self._rave27package.fetch_offline_content(env)
    self._rave3package.fetch_offline_content(env)
  
  ##
  # Returns this packages version
  # @return: the package version
  #
  def version(self):
    return self._currentpackage.version()
  
  ##
  # Returns this packages name
  # @return: the package name
  def name(self):
    return self._currentpackage.name()
  
  ##
  # Return the dependencies for this package
  # @return: the dependencies for this package
  #
  def dependencies(self):
    return self._currentpackage.dependencies()

  ##
  # Returns if this package is remembered or not
  # @return: True if remembered and False if not
  def isremembered(self):
    return True

  ## Sets if we should enable py3 support or not
  # @param usepy3: if py3 should be enabled or not
  #
  def enablePython3(self, usepy3):
    if usepy3 == True:
      self._currentpackage = self._rave3package
    else:
      self._currentpackage = self._rave27package
