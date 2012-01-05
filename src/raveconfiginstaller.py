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

Node configuration

'''

import os
import shutil
import time

from installer import installer

class raveconfiginstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(raveconfiginstaller, self).__init__(package, None)

  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    if not env.isExcluded("RAVE"):
      self._create_quality_registry(env)
    
  ##
  # Creates the quality registry for the various quality plugins that
  # belongs to the different modules
  # @param env: the build environment
  #
  def _create_quality_registry(self, env):
    dst = env.expandArgs("$PREFIX/rave/etc/rave_pgf_quality_registry.xml")
    backup = dst + "%s.bak" % time.strftime("%Y%m%dT%H%M%S")
    if os.path.exists(dst):
      shutil.move(dst, backup)
    
    outfile = open(dst, "w")
    outfile.write("""<?xml version='1.0' encoding='UTF-8'?>
<rave-pgf-quality-registry>
  <quality-plugin name="rave-overshooting" module="rave_overshooting_quality_plugin" class="rave_overshooting_quality_plugin"/>""")

    if not env.isExcluded("BROPO"):
      outfile.write("""
  <quality-plugin name="ropo" module="ropo_quality_plugin" class="ropo_quality_plugin"/>""")
      
    if not env.isExcluded("BEAMB"):
      outfile.write("""
  <quality-plugin name="beamb" module="beamb_quality_plugin" class="beamb_quality_plugin"/>""")

    outfile.write("""
</rave-pgf-quality-registry>
""")
  