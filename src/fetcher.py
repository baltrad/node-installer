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

Super class for all fetchers.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-21
'''
from InstallerException import InstallerException
import os

##
# Fectcher super class
class fetcher(object):
  
  ##
  # Constructor
  def __init__(self):
    pass
  
  ##
  # Fetches the software in some way. Requires that subclass
  # has implemented dofetch.
  # @param package: the package to fetch
  # @param env: The build environment
  # @return the file or directory name of the fetched package
  #
  def fetch(self, package, env=None):
    cdir = os.getcwd()
    try:
      return self.dofetch(package, env)
    finally:
      os.chdir(cdir)

  ##
  # Fetches the offline content in some way. Requires that subclass
  # has implemented fetch_offline_content
  # @param package: the package to fetch
  # @param env: the build environment
  #
  def fetch_offline_content(self, package, env=None):
    self.dofetch_offline_content(package, env)

  ##
  # Cleans up the related software
  # @param package: the package to fetch
  # @param env: the build environment
  #
  def clean(self, package, env=None):
    cdir = os.getcwd()
    try:
      self.doclean(package, env)
    finally:
      os.chdir(cdir)

  ##
  # Fetches the software in some way.
  # @param package: the package to fetch
  # @param env: The build environment
  # @return the file or directory name of the fetched package
  #
  def dofetch(self, package, env=None):
    raise InstallerException, "Fetcher does not implement dofetch"

  ##
  # Fetches the offline content in some way
  # @param package: the package to fetch
  # @param env: the build environment
  #
  def dofetch_offline_content(self, package, env=None):
    raise InstallerException, "Fetcher does not implement dofetch_offline_content"

  ##
  # Cleans the software in some way.
  # @param package: the package to fetch
  # @param env: The build environment
  #
  def doclean(self, package, env=None):
    raise InstallerException, "Fetcher does not implement doclean"
  
