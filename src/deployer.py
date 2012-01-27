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
import version
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
    if not os.path.islink(os.path.join(dirname, file)):
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
    if not os.path.islink(os.path.join(dirname, file)):
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

    super(deployer, self).__init__(package, oenv)

    self.node_version = version.get_node_version()
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    script = env.getNodeScript()
    
    if not os.path.exists(env.expandArgs("$TPREFIX/ant/lib/catalina-ant.jar")):
      shutil.copyfile(env.expandArgs("$TPREFIX/tomcat/lib/catalina-ant.jar"), env.expandArgs("$TPREFIX/ant/lib/catalina-ant.jar"))
    
    self._setup_permissions(env)

    script.restart(node=True)
    
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
      self._write_dex_jdbc_properties(env)
      self._write_dex_fc_properties(env)
      self._write_db_properties(env)
      self._copy_dex_default_properties(env)
      self._copy_dex_user_properties(env)
      self._write_dex_version_properties()
      self._write_bdb_bean_config(env)
      self._insert_help_documentation(env)
      os.chdir("..")
      ocode = subprocess.call(env.expandArgs("$JDKHOME/bin/jar cf %s -C %s/ ."%(tmpwar,foldername)), shell=True)
      if ocode != 0:
        raise InstallerException, "Could not pack war"
      self._deploywar(env, tmpwarpath)
    finally:
      os.chdir(cdir)
      shutil.rmtree(tmppath, True)
    
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
  def _write_dex_jdbc_properties(self, env):
    filename = "./WEB-INF/classes/eu/baltrad/dex/util/dex.jdbc.properties"
    fp = open(filename, "w")
    fp.write(env.expandArgs("""
#Autogenerated by install script
jdbc.connection.driver_class=org.postgresql.Driver
jdbc.connection.dburi=jdbc:postgresql://$DBHOST/$DBNAME
jdbc.connection.username=$DBUSER
jdbc.connection.password=$DBPWD
jdbc.connection.pool_size=5
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
database.uri=http://localhost:$BDB_PORT
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
  # Copies and replaces all relevant entries in the property file
  # automatically.
  # @param env: the build environment
  def _copy_dex_config_property_file(self, env, configfile):
    import re
    # already installed version... 
    source1 = env.expandArgs("$TPREFIX/tomcat/webapps/BaltradDex/WEB-INF/conf/%s"%configfile)
    source2 = "./WEB-INF/conf/%s"%configfile
    lines = []
    if os.path.exists(source1):
      fp = open(source1)
      lines = fp.readlines()
      fp.close()
    elif os.path.exists(source2):
      fp = open(source2)
      lines = fp.readlines()
      fp.close()
    
    outlines = []
    for line in lines:
      if line.find("#Autogenerated by install script") >= 0 or line.find("software.version=") >= 0 or line.strip() == "":
        continue # Skip these two lines, they will be first anyway
      oline = re.sub("^\s*key.alias\s*=\s*.*",env.expandArgs("key.alias=$NODENAME"),line)
      oline = re.sub("^\s*node.name\s*=\s*.*",env.expandArgs("node.name=$NODENAME"),oline)
      oline = re.sub("^\s*keystore.directory\s*=\s*.*",env.expandArgs("keystore.directory=$KEYSTORE"),oline)
      outlines.append(oline)
      
    filename = "./WEB-INF/conf/%s"%configfile
    fp = open(filename, "w")
    fp.write("""
#Autogenerated by install script
software.version=%s
""" % self.node_version)
    for line in outlines:
      fp.write(line)
    fp.close()

  ##
  # Copies and replaces the relevant entries in the dex.default.properties file.
  # @param env: the build environment
  #    
  def _copy_dex_default_properties(self, env):
    self._copy_dex_config_property_file(env, "dex.default.properties")
    
  ##
  # Copies and replaces the relevant entries in the dex.user.properties file.
  # @param env: the build environment
  #    
  def _copy_dex_user_properties(self, env):
    self._copy_dex_config_property_file(env, "dex.user.properties")

  ##
  # writes the dex.version.properties file
  #
  def _write_dex_version_properties(self):
    filename = "./WEB-INF/conf/dex.version.properties"
    fp = open(filename, "w")
    fp.write("""
#Autogenerated by install script
software.version=%s
""" % self.node_version)
    fp.close()

  ##
  # Writes the bdb.xml file
  #
  def _write_bdb_bean_config(self, env):
    filename = "./WEB-INF/bdb.xml"
    conf = [
      '<?xml version="1.0" encoding="UTF-8"?>',
      '<beans xmlns="http://www.springframework.org/schema/beans"',
      '       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
      '       xsi:schemaLocation="http://www.springframework.org/schema/beans',
      '       http://www.springframework.org/schema/beans/spring-beans-2.5.xsd">',
    ]

    auth = env.getArg("BDB_AUTH")
    if auth == "keyczar":
      conf.extend([
        '  <bean id="bdb_auth" class="eu.baltrad.bdb.db.rest.KeyczarAuthenticator">',
        '    <constructor-arg index="0" value="$KEYSTORE/$NODENAME.priv" />',
        '    <constructor-arg index="1" value="$NODENAME" />',
        '  </bean>',
      ])
    elif auth == "noauth":
      conf.extend([
        '  <bean id="bdb_auth" class="eu.baltrad.bdb.db.rest.NullAuthenticator"/>',
      ])
    else:
      raise InstallerException, "unrecognized BDB_AUTH: %s" % auth

    conf.extend([
      '  <bean id="bdb_db" class="eu.baltrad.bdb.db.rest.RestfulDatabase" >',
      '    <constructor-arg value="$${database.uri}" />',
      '    <constructor-arg ref="bdb_auth" />',
      '  </bean>',
    ])

    storage = env.getArg("BDB_STORAGE")
    if storage == "db":
      conf.extend([
        '  <bean id="bdb_storage" class="eu.baltrad.bdb.storage.CacheDirStorage">',
        '    <constructor-arg index="0" value="$${data.storage.folder}" />',
        '    <constructor-arg index="1" value="1000" /> <!-- cache size -->',
        '  </bean>',
      ])
    elif storage == "fs":
      conf.extend([
        '  <bean id="bdb_storage" class="eu.baltrad.bdb.storage.ServerFileStorage">',
        '    <constructor-arg index="0" value="$${data.storage.folder}" />',
        '    <constructor-arg index="1" value="3" /> <!-- number of layers -->',
        '  </bean>',
      ])
    else:
      raise InstallerException, "unrecognized BDB_AUTH: %s" % auth

    conf.extend([
      '  <bean id="bdb_file_catalog" class="eu.baltrad.bdb.BasicFileCatalog">',
      '    <constructor-arg ref="bdb_db" />',
      '    <constructor-arg ref="bdb_storage" />',
      '  </bean>',
      '</beans>'
    ])
    conf = [env.expandArgs(c) for c in conf]
    fp = open(filename, "w")
    fp.write("\n".join(conf))
    fp.close()

  ##
  # Returns all files that are in a directory. It will not
  # return directories or links.
  # @param dir: The directory name
  # @return: a list of files
  def _get_files_in_directory(self, dir):
    import glob
    result = []
    files = glob.glob("%s/*"%dir)
    
    for file in files:
      if os.path.isfile(file) and not os.path.islink(file):
        result.append(file)
    
    return result
  
  ##
  # Returns all directories that are in a directory. It will not
  # return files or links.
  # @param dir: The directory name
  # @return: a list of files
  def _get_dirs_in_directory(self, dir):
    import glob
    result = []
    files = glob.glob("%s/*"%dir)
    
    for file in files:
      if os.path.isdir(file) and not os.path.islink(file):
        result.append(file)
    
    return result
    
  ##
  # Inserts the help documentation into the bundle
  # @param env: the build environment
  def _insert_help_documentation(self, env):
    pth = env.expandArgs("$PREFIX/doc")
    files = self._get_files_in_directory(pth)
    dirs = self._get_dirs_in_directory(pth)
    
    for f in files:
      shutil.copy(f, "./help/")
    
    for d in dirs:
      basename=os.path.basename(d)
      shutil.copytree(d, "./help/%s"%basename)
  
  ##
  # Deploys the war
  def _deploywar(self, env, warpath):
    args = "-Dmgr.url=$TOMCATURL/manager -Dmgr.path=/BaltradDex -Dmgr.username=admin -Dmgr.password=$TOMCATPWD"
    args = "%s -Dwarfile=%s"%(args, warpath)
    buildfile = "%s/etc/war-deployer.xml"%env.getInstallerPath()
    
    # remove keystore just in case we are redeploying,
    # redeployment seems to recursively remove symlinked directories
    self._unlink_keystore(env)
    
    #print env.expandArgs("Calling: $TPREFIX/ant/bin/ant -f %s %s deploy"%(buildfile, args))
    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -f %s %s deploy"%(buildfile, args)), shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to deploy system"   
  
  ##
  # 
  def _unlink_keystore(self, env):
    deployed_confdir = env.expandArgs("$TPREFIX/tomcat/webapps/BaltradDex/WEB-INF/conf/")
    keystore_dst = os.path.join(deployed_confdir, ".dex_keystore.jks")
    if os.path.exists(keystore_dst):
        print "unlinking", keystore_dst
        os.unlink(keystore_dst)
  
