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

This is the final step. The system is stopped and started.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2012-01-04
'''
from installer import installer
from InstallerException import InstallerException
import subprocess

##
# The node starter
class finished(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(finished, self).__init__(package, None)

  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    import time, sys
    
    ocode = subprocess.call(env.expandArgs("$PREFIX/bin/bltnode --all stop"), shell=True)
    if ocode != 0:
      raise InstallerException, "Could not stop node"

    sys.stdout.write("Waiting for system to halt (5 seconds) ")
    sys.stdout.flush()
    for i in range(5):
      time.sleep(1)
      sys.stdout.write(".")
      sys.stdout.flush()
    print ""

    ocode = subprocess.call(env.expandArgs("$PREFIX/bin/bltnode --all start"), shell=True)
    if ocode != 0:
      raise InstallerException, "Could not start node"

    print ""
    print "===== SUCCESS ======"
    print "System has sucessfully been installed and started"
    print "You should be able to access the system by navigating a browser to:"
    print env.expandArgs("$TOMCATURL/BaltradDex")
    print ""
    print ""
    print "Your BDB sources might not be up-to-date. You can import them from"
    print "Rave's radar-db with the following command:"
    print ""
    print env.expandArgs("$PREFIX/baltrad-db/bin/baltrad-bdb-client \\")
    print "  import_sources \\"
    print env.expandArgs("  --url=http://localhost:$BDB_PORT \\")
    print env.expandArgs("  --dry-run \\")
    print env.expandArgs("  $PREFIX/rave/config/odim_source.xml")
    print ""
    print "You can omit some changes by adding '--ignore=src' to the command."  
    print "Once you are satisified with what the importer will do, omit the"
    print "'--dry-run' switch and let it work on the actual database."
    print ""
    print "Before running the command you might need to setup your environment"
    print "by for example sourcing"
    print env.expandArgs("$PREFIX/etc/bltnode.rc")
    print ""
    
