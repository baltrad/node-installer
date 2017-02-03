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
import getpass, pwd, stat, sys

##
# Function that performs chmod. Called by a walker
# @param mode: the mode
# @param dirname: name of directory
# @param fnames: the filenames in the directory
#
def _walk_chmod(mode, dirname, fnames):
  os.chmod(dirname, mode)
  for f in fnames:
    if not os.path.islink(os.path.join(dirname, f)):
      os.chmod(os.path.join(dirname, f), mode)

##
# Function that performs chown. Called by a walker
# @param mode: the uid and gid in numerical form
# @param dirname: name of directory
# @param fnames: the filenames in the directory
#
def _walk_chown(uidgid, dirname, fnames):
  os.chown(dirname, uidgid[0], uidgid[1])
  for f in fnames:
    if not os.path.islink(os.path.join(dirname, f)):
      os.chown(os.path.join(dirname, f), uidgid[0], uidgid[1])

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
    
    #if not os.path.exists(env.expandArgs("$TPREFIX/ant/lib/catalina-ant.jar")):
    shutil.copyfile(env.expandArgs("$TPREFIX/tomcat/lib/catalina-ant.jar"), env.expandArgs("$TPREFIX/ant/lib/catalina-ant.jar"))
    # New files to copy
    shutil.copyfile(env.expandArgs("$TPREFIX/tomcat/lib/tomcat-coyote.jar"), env.expandArgs("$TPREFIX/ant/lib/tomcat-coyote.jar"))
    shutil.copyfile(env.expandArgs("$TPREFIX/tomcat/lib/tomcat-util.jar"), env.expandArgs("$TPREFIX/ant/lib/tomcat-util.jar"))
    shutil.copyfile(env.expandArgs("$TPREFIX/tomcat/bin/tomcat-juli.jar"), env.expandArgs("$TPREFIX/ant/lib/tomcat-juli.jar"))
    
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
      ocode = subprocess.call(env.expandArgs("$JDKHOME/bin/jar -xvf %s  > /dev/null 2>&1"%warFile), shell=True)
      if ocode != 0:
        raise InstallerException, "Could not extract war"
      self._write_dex_fc_properties(env)
      self._write_db_properties(env)
      self._copy_dex_properties(env)
      self._write_bdb_bean_config(env)
      self._update_appcontext_for_secure_comm(env)
      self._insert_help_documentation(env)
      os.chdir("..")
      ocode = subprocess.call(env.expandArgs("$JDKHOME/bin/jar cf %s -C %s/ ."%(tmpwar,foldername)), shell=True)
      if ocode != 0:
        raise InstallerException, "Could not pack war"
      self._deploywar(env, tmpwarpath)
      self._modify_db_properties_permission(env)
    finally:
      os.chdir(cdir)
      shutil.rmtree(tmppath, True)
    
  ##
  # Setups the appropriate tomcat permissions on the tomcat installation or
  # gives information to the user that it is necessary
  # @param env: the build environment
  #
  def _setup_permissions(self, env):
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
  # Creates the fc properties property file
  # @param env: the build environment
  #
  def _write_dex_fc_properties(self, env):
    filename = "./WEB-INF/classes/resources/dex.fc.properties"
    fp = open(filename, "w")
    if "BDB" not in env.getArg("SUBSYSTEMS"):
      fp.write(env.expandArgs("""
#Autogenerated by install script
database.uri=$BDB_URI
"""))
    else:      
      fp.write(env.expandArgs("""
#Autogenerated by install script
database.uri=http://localhost:$BDB_PORT
"""))
      
    fp.write(env.expandArgs("""
# File catalog data storage directory
data.storage.folder=${DATADIR}
"""))
    fp.write(env.expandArgs("""
# Keyczar key to communicate with node
database.keyczar.key=$KEYSTORE/$NODENAME.priv
# Name of the node
database.keyczar.name=$NODENAME
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
    
    
  def _modify_db_properties_permission(self, env):
    filename = env.expandArgs("$TPREFIX/tomcat/webapps/BaltradDex/db.properties")
    if os.path.exists(filename):
      try:
        os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR)
      except:
        pass
  
  ##
  # Copies and replaces all relevant entries in the property file
  # automatically.
  # @param env: the build environment
  def _copy_dex_config_property_file(self, env):
    import re
    # already installed version...
    if not os.path.exists(env.expandArgs("$TPREFIX/tomcat/webapps/BaltradDex/dex.properties")):
      oldvariant = env.expandArgs("$TPREFIX/tomcat/webapps/BaltradDex/WEB-INF/conf/dex.user.properties")
      if os.path.exists(oldvariant):
        shutil.move(oldvariant, env.expandArgs("$TPREFIX/tomcat/webapps/BaltradDex/dex.user.properties"))
      
      oldvariant = env.expandArgs("$TPREFIX/tomcat/webapps/BaltradDex/dex.user.properties")
      if os.path.exists(oldvariant):
        newfname = env.expandArgs("$TPREFIX/tomcat/webapps/BaltradDex/dex.properties")
        shutil.move(oldvariant, newfname)
        # We need to add a couple of more entries to the properties file
        fp = open(newfname, "a")
        fp.write("""
organization.name=Organization
organization.unit=Department
organization.locality=City
organization.state=Country
organization.country_code=XX

""")
        fp.close()
    
    source1 = env.expandArgs("$TPREFIX/tomcat/webapps/BaltradDex/dex.properties")
    source2 = "dex.properties"
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
      
    filename = "dex.properties"
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
  def _copy_dex_properties(self, env):
    self._copy_dex_config_property_file(env)

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
      '       http://www.springframework.org/schema/beans/spring-beans-4.2.xsd">',
    ]

    auth = env.getArg("BDB_AUTH")
    if auth == "keyczar":
      conf.extend([
        '  <bean id="bdb_auth" class="eu.baltrad.bdb.db.rest.KeyczarAuthenticator">',
        '    <constructor-arg index="0" value="$${database.keyczar.key}" />',
        '    <constructor-arg index="1" value="$${database.keyczar.name}" />',
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
      '    <constructor-arg value="20" />',  
      '    <constructor-arg value="$BDB_FILEENTRY_CACHE_SIZE" /> <!-- file entry cache size -->',
      '  </bean>',
    ])

    storage = env.getArg("BDB_STORAGE")
    if storage == "db":
      conf.extend([
        '  <bean id="bdb_storage"',
        '        class="eu.baltrad.bdb.storage.CacheDirStorage"',
        '        init-method="init">',
        '    <constructor-arg index="0" value="$${data.storage.folder}" />',
        '    <constructor-arg index="1" value="$BDB_CACHE_SIZE" /> <!-- cache size -->',
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

  def _update_appcontext_for_secure_comm(self, env):
    httpfwd = None
    httpsfwd = None
    if env.hasArg("TOMCATFWDPORTS"):
      tokens = env.getArg("TOMCATFWDPORTS").split(",")
      httpfwd = tokens[0]
      httpsfwd = tokens[1]
      
    # First, remove any previous security port mapping settings
    ifp = open("./WEB-INF/applicationContext.xml", "r")
    ofp = open("./WEB-INF/applicationContext.xml.tmp", "w")
    ilines = ifp.readlines()
    for tl in ilines:
      if tl.find("<security:port-mapping") >= 0: #Also affects port-mappings
        tl = "\n"
      if tl.find("</security:port-mappings>") >= 0:
        tl = "\n"
      ofp.write(tl)
    ifp.close()
    ofp.close()
    
    # Next add security port mapping if wanted, add it right after security:http
    ifp = open("./WEB-INF/applicationContext.xml.tmp", "r")
    ofp = open("./WEB-INF/applicationContext.xml", "w")
    ilines = ifp.readlines()
    for tl in ilines:
      if tl.find("<security:http") >= 0:
        ofp.write(tl)
        ofp.write("<!-- Autogenerated by the node-installer -->\n")
        ofp.write("<security:port-mappings>\n")
        ofp.write("<security:port-mapping http=\"%s\" https=\"%s\"/>\n" % (env.getArg("TOMCATPORT"), env.getArg("TOMCATSECUREPORT")))
        if httpfwd != None:
          ofp.write("<security:port-mapping http=\"%s\" https=\"%s\"/>\n" % (httpfwd, httpsfwd))
        ofp.write("</security:port-mappings>\n")
        ofp.write("<!-- End of Autogenerated by the node-installer -->\n")
      else:
        ofp.write(tl)
    ifp.close()
    ofp.close()

  ##
  # Returns all files that are in a directory. It will not
  # return directories or links.
  # @param dir: The directory name
  # @return: a list of files
  def _get_files_in_directory(self, d):
    import glob
    result = []
    files = glob.glob("%s/*"%d)
    
    for f in files:
      if os.path.isfile(f) and not os.path.islink(f):
        result.append(f)
    
    return result
  
  ##
  # Returns all directories that are in a directory. It will not
  # return files or links.
  # @param dir: The directory name
  # @return: a list of files
  def _get_dirs_in_directory(self, d):
    import glob
    result = []
    files = glob.glob("%s/*"%d)
    
    for f in files:
      if os.path.isdir(f) and not os.path.islink(f):
        result.append(f)
    
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
    args = "-Dmgr.url=$TOMCATURL/manager/text -Dmgr.path=/BaltradDex -Dmgr.username=admin -Dmgr.password=$TOMCATPWD"
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
  
