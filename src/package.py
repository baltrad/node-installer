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

Defines a package that should be installed.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-20
'''

##
# The package/module class
#
class package(object):
  ##
  # Constructor
  # @param name: the name of the package, e.g. ZLIB
  # @param version: the version of the package, e.g. 1.2.4
  # @param fetcher: a fetcher, that always returns a directory
  # @param depends: if this package depends on any other packages
  # @param remembered: if this package should be remembered to have been installed or not
  # @param extra_attrs: extra attributes to define for the package
  #
  def __init__(self, name, version, fetcher=None, depends=[], remembered=True,
               extra_attrs={}):
    self._name = name
    self._version = version
    self._fetcher = fetcher
    self._dependencies = []
    if depends != None:
      self._dependencies = depends
    self._remembered = remembered
    for k, v in extra_attrs.items():
        setattr(self, k, v)
    
  ##
  # Executes the fetcher
  # @param env: the build environment
  # @return: a directory where the package can be accessed
  #
  def fetch(self, env=None):
    return self._fetcher.fetch(self, env=env)

  ##
  # Fetches the 'offline' content for this package
  # @param env: the build environment
  #  
  def fetch_offline_content(self, env=None):
    if self._fetcher != None:
      self._fetcher.fetch_offline_content(self, env=env)

  ##
  # Executes the fetcher cleanup method
  # @param env: the build environment
  #
  def clean(self, env=None):
    if self._fetcher != None:
      self._fetcher.clean(self, env=env)
  
  ##
  # Returns this packages version
  # @return: the package version
  #
  def version(self):
    return self._version
  
  ##
  # Returns this packages name
  # @return: the package name
  def name(self):
    return self._name
  
  ##
  # Return the dependencies for this package
  # @return: the dependencies for this package
  #
  def dependencies(self):
    return self._dependencies

  ##
  # Returns if this package is remembered or not
  # @return: True if remembered and False if not
  def isremembered(self):
    return self._remembered
  
