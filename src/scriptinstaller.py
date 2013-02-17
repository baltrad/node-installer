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

Installs the node scripts. Depends on the nodescripts object for
getting the different scripts

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-15
'''
from installer import installer
from InstallerException import InstallerException
import shutil, os, stat

##
# The script installer
class scriptinstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(scriptinstaller, self).__init__(package, None)
  
    
  ##
  # Checks if the provided dir exists and if not creates it
  # @param dir: the dir name
  def _createdir(self, dir):
    if not os.path.exists(dir):
      os.mkdir(dir)
    elif not os.path.isdir(dir):
      raise InstallerException, "%s exists but is not a directory"%dir
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    script = env.getNodeScript()
    
    self._createdir(env.expandArgs("$PREFIX/bin"))
    self._createdir(env.expandArgs("$PREFIX/etc"))
    
    shutil.copyfile(script.get_bltnode_script_path(), env.expandArgs("$PREFIX/bin/bltnode"))
    os.chmod(env.expandArgs("$PREFIX/bin/bltnode"), stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)

    shutil.copyfile(script.get_initd_script_path(), env.expandArgs("$PREFIX/etc/bltnode.init.d"))
    os.chmod(env.expandArgs("$PREFIX/etc/bltnode.init.d"), stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)

    shutil.copyfile(script.get_rave_initd_script_path(), env.expandArgs("$PREFIX/etc/ravepgf.init.d"))
    os.chmod(env.expandArgs("$PREFIX/etc/ravepgf.init.d"), stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    
    shutil.copyfile(script.get_node_source_path(), env.expandArgs("$PREFIX/etc/bltnode.rc"))
    os.chmod(env.expandArgs("$PREFIX/etc/bltnode.rc"), stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)

    shutil.copyfile("%s/bin/baltrad_post_config.py"%env.getInstallerPath(), env.expandArgs("$PREFIX/bin/baltrad_post_config"))
    os.chmod(env.expandArgs("$PREFIX/bin/baltrad_post_config"), stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)


