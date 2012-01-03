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

Defines a node module that can be used by the node package

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-09
'''
from node_versions import versions

class nodedefinition:
  _gituri = None
  _version = None
  _branch = None
  def __init__(self, gituri, version, branch=None):
    self._gituri = gituri
    self._version = version
    self._branch = branch
  
  def geturi(self):
    return self._gituri
  
  def getversion(self):
    return self._version
  
  def getbranch(self):
    return self._branch

_REPOS = {
  "HLHDF": "$GITREPO:hlhdf.git",
  "BALTRAD-DB": "$GITREPO:baltrad-db.git",
  "BEAST": "$GITREPO:beast.git",
  "BALTRAD-DEX": "$GITREPO:BaltradDex.git",
  "RAVE": "$GITREPO:rave.git",
  "RAVE-GMAP": "$GITREPO:GoogleMapsPlugin.git",
  "BROPO": "$GITREPO:bropo.git",
  "BBUFR": "$GITREPO:bbufr.git",
  "BEAMB": "$GITREPO:beamb.git"
}

PACKAGES = [
  "HLHDF", "BALTRAD-DB", "BEAST", "BALTRAD-DEX", "RAVE", "RAVE-GMAP", "BROPO", "BBUFR", "BEAMB"
]

NODE_REPOSITORY={}

for pkg in PACKAGES:
    NODE_REPOSITORY[pkg] = nodedefinition(_REPOS[pkg], versions[pkg])

