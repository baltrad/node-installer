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

Database table installer. Will install & upgrade database tables.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-14
'''
from installer import installer
import os, subprocess
from osenv import osenv
from InstallerException import InstallerException

##
# The database installer
#
class dbinstaller(installer):
  ##
  # Constructor
  # Installs the beast package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"ANT_HOME":"$TPREFIX/ant",
                    "JAVA_HOME":"$JDKHOME",
                    "PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$PREFIX/hlhdf/lib:$$LD_LIBRARY_PATH"},
                    defaultosenv={"LD_LIBRARY_PATH":""})
    super(dbinstaller, self).__init__(pkg, oenv)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    if env.hasArg("EXCLUDEDB") and env.getArg("EXCLUDEDB") == True:
      print "Excluded: Database table installation"
      return
    dbargs = "-Ddb.user=$DBUSER -Ddb.pwd=$DBPWD -Ddb.host=$DBHOST -Ddb.name=$DBNAME"
    args = "%s -Dbaltrad.beast.path=$PREFIX/beast -Dbaltrad.dex.path=$PREFIX/BaltradDex" % dbargs
    
    if not os.path.isdir(env.expandArgs("$DATADIR")):
      os.mkdir(env.expandArgs("$DATADIR"))
    
    args = "%s -Ddb.jar=%s/etc/postgresql/postgresql-8.4-701.jdbc4.jar"%(args, env.getInstallerPath())
    buildfile = "%s/etc/install_db.xml"%env.getInstallerPath()
    
    if env.hasArg("REINSTALLDB") and env.getArg("REINSTALLDB") == True:
      ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -f %s %s drop-db"%(buildfile,args)), shell=True)
      if ocode != 0:
        raise InstallerException, "Failed to drop database tables"
      
      ocode = subprocess.call([
        env.expandArgs("$PREFIX/baltrad-db/bin/baltrad-bdb-drop)"),
        env.expandArgs("--conf=$PREFIX/etc/bltnode.properties")
      ])
      if ocode != 0:
        raise InstallerException, "Faield to drop BDB"
        
    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -f %s %s install-db"%(buildfile,args)), shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to install database tables"

    ocode = subprocess.call([
      env.expandArgs("$PREFIX/baltrad-db/bin/baltrad-bdb-create)"),
      env.expandArgs("--conf=$PREFIX/etc/bltnode.properties")
    ])
    if ocode != 0:
      raise InstallerException, "Faield to create BDB"
    

##
# The database upgrader, should always be executed so setup package for that
#
class dbupgrader(dbinstaller):
  ##
  # Constructor
  # Performs the db upgrade
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"ANT_HOME":"$TPREFIX/ant",
                    "JAVA_HOME":"$JDKHOME",
                    "PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$PREFIX/hlhdf/lib:$$LD_LIBRARY_PATH"},
                    defaultosenv={"LD_LIBRARY_PATH":""})
    super(dbupgrader, self).__init__(pkg, oenv)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dbargs = "-Ddb.user=$DBUSER -Ddb.pwd=$DBPWD -Ddb.host=$DBHOST -Ddb.name=$DBNAME"
    args = "%s -Dbaltrad.db.path=$PREFIX/baltrad-db -Dbaltrad.beast.path=$PREFIX/beast -Dbaltrad.dex.path=$PREFIX/BaltradDex" % dbargs
    
    args = "%s -Ddb.jar=%s/etc/postgresql/postgresql-8.4-701.jdbc4.jar"%(args, env.getInstallerPath())
    
    buildfile = "%s/etc/install_db.xml"%env.getInstallerPath()
    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -f %s %s upgrade-db"%(buildfile,args)), shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to upgrade db"

    ocode = subprocess.call([
      env.expandArgs("$PREFIX/baltrad-db/bin/baltrad-bdb-upgrade"),
      env.expandArgs("--conf=$PREFIX/etc/bltnode.properties")
    ])
    if ocode != 0:
      raise InstallerException, "Failed to upgrade BDB"
