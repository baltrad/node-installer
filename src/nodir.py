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

A special class for indicating when you should not change dir during
installation. Usage is typically when you are fetching a resource that
should be directly copied some where.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-25
'''
from fetcher import fetcher

##
# Nodir class
class nodir(fetcher):
  _fetcher = None
  
  ##
  # Constructor
  # @param fetcher: the fetcher that this class should execute
  #
  def __init__(self, fetcher=None):
    super(nodir, self).__init__()
    self._fetcher = fetcher
  
  ##
  # Executes the fetcher and then return ".".
  # @param package: the package to fetch
  # @param env: the build environment
  # @return: "."
  def dofetch(self, package, env=None):
    if self._fetcher != None:
      self._fetcher.fetch(package, env)
    return "."
  
  ##
  # Executes the clean function in the fetcher
  # @param package: the package to clean
  # @param env: the build environment
  #
  def doclean(self, package, env=None):
    if self._fetcher != None:
      self._fetcher.clean(package, env)
 
  ##
  # Executes the fetcher
  # @param package: the package to fetch
  # @param env: the build environment
  #  
  def dofetch_offline_content(self, package, env=None):
    if self._fetcher != None:
      self._fetcher.dofetch_offline_content(package, env)
