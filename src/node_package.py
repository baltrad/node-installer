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

Node specific package which is more suitable for defining our baltrad node
specific packages since we are more prone to create new versions and
also the possibility have have offline mode installation.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-09
'''
from package import package
from nodedefinition import NODE_REPOSITORY
from gitfetcher import gitfetcher

##
# The package/module class
#
class node_package(package):
  
  ##
  # Constructor
  # @param name: the name of the package, e.g. ZLIB
  # @param version: the version of the package, e.g. 1.2.4
  # @param fetcher: a fetcher, that always returns a directory
  # @param depends: if this package depends on any other packages
  #
  def __init__(self, name, depends=[]):
    ver = NODE_REPOSITORY[name].getversion()
    uri = NODE_REPOSITORY[name].geturi()
    branch = NODE_REPOSITORY[name].getbranch()
    fetcher = gitfetcher(uri, ver, branch)
    super(node_package, self).__init__(name, ver, fetcher, depends)
  
  ##
  # Executes the fetcher. Can both work in offline and online mode
  # @return: a directory where the package can be accessed
  #
  def fetch(self, env=None):
    return package.fetch(self, env)
