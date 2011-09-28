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

Deployer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-15
'''
from installer import installer
from InstallerException import InstallerException
import subprocess
import shutil, os,tempfile
from osenv import osenv

##
# Function that performs chmod. Called by a walker
# @param mode: the mode
# @param dirname: name of directory
# @param fnames: the filenames in the directory
#
def _walk_chmod(mode, dirname, fnames):
  os.chmod(dirname, mode)
  for file in fnames:
    os.chmod(os.path.join(dirname, file), mode)

##
# Function that performs chown. Called by a walker
# @param mode: the uid and gid in numerical form
# @param dirname: name of directory
# @param fnames: the filenames in the directory
#
def _walk_chown(uidgid, dirname, fnames):
  os.chown(dirname, uidgid[0], uidgid[1])
  for file in fnames:
    os.chown(os.path.join(dirname, file), uidgid[0], uidgid[1])

##
# The deployer
class deployer(installer):
  ##
  # Constructor
  #
  def __init__(self, package, oenv=None):
    if oenv == None:
      oenv = osenv({"ANT_HOME":"$TPREFIX/ant",
                    "JAVA_HOME":"$JDKHOME",
                    "PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":""})

    super(deployer, self).__init__(package, None)
  
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    script = env.getNodeScript()
    
    script.restart(node=True)
    
    if not os.path.exists(env.expandArgs("$TPREFIX/ant/lib/catalina-ant.jar")):
      shutil.copyfile(env.expandArgs("$TPREFIX/tomcat/lib/catalina-ant.jar"), env.expandArgs("$TPREFIX/ant/lib/catalina-ant.jar"))
    
    self._link_baltrad_db(env)
    self._setup_permissions(env)
    
    tmppath = tempfile.mkdtemp(prefix='baltradnode')
    foldername = os.path.basename(tmppath)
    
    fpd, tmpwarpath = tempfile.mkstemp(suffix=".war", prefix="deploy")
    try:
      os.close(fpd)
    except:
      pass
    tmpwar = os.path.basename(tmpwarpath)
    
    warFile = env.expandArgs("$PREFIX/BaltradDex/bin/BaltradDex.war")
    if env.hasArg("WARFILE") and env.getArg("WARFILE") != None:
      warFile = env.getArg("WARFILE")
    
    cdir = os.getcwd()
    os.chdir(tmppath)
    
    try:
      ocode = subprocess.call(env.expandArgs("$JDKHOME/bin/jar -xvf %s"%warFile), shell=True)
      if ocode != 0:
        raise InstallerException, "Could not extract war"
      self._write_dex_hibernate_properties(env)
      self._write_dex_fc_properties(env)
      self._write_db_properties(env)
      os.chdir("..")
      ocode = subprocess.call(env.expandArgs("$JDKHOME/bin/jar cf %s -C %s/ ."%(tmpwar,foldername)), shell=True)
      if ocode != 0:
        raise InstallerException, "Could not pack war"
      self._deploywar(env, tmpwarpath)
    finally:
      os.chdir(cdir)
      shutil.rmtree(tmppath, True)

  ##
  # Creates a symbolic link from baltrad dbs jbrfc.jar into tomcats lib dir
  # @param env: the build environment
  #
  def _link_baltrad_db(self, env):
    if os.path.exists(env.expandArgs("$TPREFIX/tomcat/lib/jbrfc.jar")):
      os.unlink(env.expandArgs("$TPREFIX/tomcat/lib/jbrfc.jar"))
    os.symlink(env.expandArgs("$PREFIX/baltrad-db/share/baltrad-db/java/jbrfc.jar"), env.expandArgs("$TPREFIX/tomcat/lib/jbrfc.jar"))
  
  ##
  # Setups the appropriate tomcat permissions on the tomcat installation or
  # gives information to the user that it is necessary
  # @param env: the build environment
  #
  def _setup_permissions(self, env):
    import getpass, pwd, stat, sys
    runas = env.getArg("RUNASUSER")
    if runas == "root":
      raise InstallerException, "You should not atempt to run system as root"

    obj = pwd.getpwnam(runas)

    if runas == getpass.getuser() or "root" == getpass.getuser():
      if "root" == getpass.getuser():
        os.path.walk(env.expandArgs("$TPREFIX/tomcat"), _walk_chown, [obj.pw_uid,obj.pw_gid])
      os.path.walk(env.expandArgs("$TPREFIX/tomcat/bin"), _walk_chmod, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
      os.path.walk(env.expandArgs("$TPREFIX/tomcat/webapps"), _walk_chmod, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
      os.path.walk(env.expandArgs("$TPREFIX/tomcat/logs"), _walk_chmod, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
      os.path.walk(env.expandArgs("$TPREFIX/tomcat/conf"), _walk_chmod, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    else:
      print "You must manually modify the tomcat permissions before continuing...."
      print env.expandArgs("""
chown -R $RUNASUSER:$RUNASUSER $TPREFIX/tomcat
chmod -R 555 $TPREFIX/tomcat/bin
chmod -R 755 $TPREFIX/tomcat/webapps
chmod -R 755 $TPREFIX/tomcat/logs
chmod -R 755 $TPREFIX/tomcat/conf
""")
      print "Press return when finished or write 'quit' to exit:",
      sys.stdout.flush()
      a=sys.stdin.readline().strip()
      if a == "quit":
        raise InstallerException, "Manually terminated script"

  ##
  # Creates the hibernate properties property file
  # @param env: the build environment
  #
  def _write_dex_hibernate_properties(self, env):
    filename = "./WEB-INF/classes/eu/baltrad/dex/util/dex.hibernate.properties"
    fp = open(filename, "w")
    fp.write(env.expandArgs("""
#Autogenerated by install script
hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
hibernate.connection.driver_class=org.postgresql.Driver
hibernate.connection.url=jdbc:postgresql://$DBHOST/$DBNAME
hibernate.connection.username=$DBUSER
hibernate.connection.password=$DBPWD
hibernate.connection.pool_size=10
hibernate.connection.release_mode=on_close
"""))
    fp.close()

  ##
  # Creates the fc properties property file
  # @param env: the build environment
  #
  def _write_dex_fc_properties(self, env):
    filename = "./WEB-INF/classes/eu/baltrad/dex/util/dex.fc.properties"
    fp = open(filename, "w")
    fp.write(env.expandArgs("""
#Autogenerated by install script
database.uri=postgresql://$DBUSER:$DBPWD@$DBHOST/$DBNAME
# File catalog data storage directory
data.storage.folder=${DATADIR}
# Image storage directory
image.storage.folder=images
# Image thumbs storage directory
thumbs.storage.folder=thumbs
"""))
    fp.close()    

  ##
  # Creates the db properties property file
  # @param env: the build environment
  #
  def _write_db_properties(self, env):
    filename = "./db.properties"
    fp = open(filename, "w")
    fp.write(env.expandArgs("""
#Autogenerated by install script
db.jar=postgresql-8.4-701.jdbc4.jar
db.driver=org.postgresql.Driver
db.url=jdbc:postgresql://$DBHOST/$DBNAME
db.user=$DBUSER
db.pwd=$DBPWD
"""))
    fp.close()    

  ##
  # Deploys the war
  def _deploywar(self, env, warpath):
    args = "-Dmgr.url=$TOMCATURL/manager -Dmgr.path=/BaltradDex -Dmgr.username=admin -Dmgr.password=$TOMCATPWD"
    args = "%s -Dwarfile=%s"%(args, warpath)
    buildfile = "%s/etc/war-deployer.xml"%env.getInstallerPath()
    
    #print env.expandArgs("Calling: $TPREFIX/ant/bin/ant -f %s %s deploy"%(buildfile, args))
    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -f %s %s deploy"%(buildfile, args)), shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to deploy system"
    