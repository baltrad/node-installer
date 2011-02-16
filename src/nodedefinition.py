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
from node_versions import HLHDF_VERSION, BALTRAD_DB_VERSION, BEAST_VERSION, BALTRAD_DEX_VERSION, RAVE_VERSION, RAVE_GMAP_VERSION

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


NODE_REPOSITORY={}
NODE_REPOSITORY["HLHDF"]=nodedefinition("gitosis@git.baltrad.eu:hlhdf.git", HLHDF_VERSION)
NODE_REPOSITORY["BALTRAD-DB"]=nodedefinition("gitosis@git.baltrad.eu:baltrad-db.git", BALTRAD_DB_VERSION)
NODE_REPOSITORY["BEAST"]=nodedefinition("gitosis@git.baltrad.eu:beast.git", BEAST_VERSION)
NODE_REPOSITORY["BALTRAD-DEX"]=nodedefinition("gitosis@git.baltrad.eu:BaltradDex.git", BALTRAD_DEX_VERSION)
NODE_REPOSITORY["RAVE"]=nodedefinition("gitosis@git.baltrad.eu:rave.git", RAVE_VERSION)
NODE_REPOSITORY["RAVE-GMAP"]=nodedefinition("gitosis@git.baltrad.eu:GoogleMapsPlugin.git", RAVE_GMAP_VERSION)
