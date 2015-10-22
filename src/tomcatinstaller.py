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

Tomcat specific installer.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-04
'''
from installer import installer
from InstallerException import InstallerException
import subprocess
import shutil, os

##
# The tomcat installer
class tomcatinstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(tomcatinstaller, self).__init__(package, None)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)

    if self.isTomcatRunning(env):
      raise InstallerException, "Tomcat process is running, please stop it first"

    self.patch_catalina_sh(dir, env)

    shutil.rmtree(env.expandArgs("$TPREFIX/tomcat.bak"), True)
    if os.path.isdir(env.expandArgs("$TPREFIX/tomcat")):
      shutil.move(env.expandArgs("$TPREFIX/tomcat"), env.expandArgs("$TPREFIX/tomcat.bak"))
    
    shutil.move(dir, env.expandArgs("$TPREFIX/tomcat"))

    self.write_tomcat_users(env)
    
    self.write_root_index_file(env.expandArgs("$TPREFIX/tomcat"))
    
    self.patch_server_xml(dir, env)
  
  ##
  # Checks if tomcat already is running or not by using ps
  # @param env: the build environment
  # @return: True or False
  #
  def isTomcatRunning(self, env):
    result = False
    ps = subprocess.Popen(['ps', '-edalf'], stdout=subprocess.PIPE).communicate()[0]
    processes = ps.split('\n')
    for p in processes:
      if p.find("tomcat") >= 0:
        if p.find(env.expandArgs("$TPREFIX/tomcat")) >= 0:
          result = True
    
    return result 
  
  ##
  # Creates the tomcat users file
  # @param env: the build environment
  #
  def write_tomcat_users(self, env):
    filename = "%s/conf/tomcat-users.xml" % env.expandArgs("$TPREFIX/tomcat")
    fp = open(filename, "w")
    fp.write(env.expandArgs("""<?xml version='1.0' encoding='utf-8'?>
<tomcat-users>
  <role rolename="manager"/>
  <role rolename="manager-gui"/>
  <role rolename="manager-script"/>
  <role rolename="manager-jmx"/>
  <role rolename="manager-status"/>
  <role rolename="tomcat"/>
  <role rolename="admin"/>
  <user username="admin" password="${TOMCATPWD}" roles="admin,tomcat,manager,manager-gui, manager-jmx, manager-status, manager-script"/>
</tomcat-users>
    """))
    fp.close()
  
  ##
  # Writes the index.html file
  # @param troot: the tomcat root directory
  #
  def write_root_index_file(self, troot):
    filename = "%s/webapps/ROOT/index.html"%troot
    fp = open(filename, "w")
    fp.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
  <HEAD>
    <TITLE></TITLE>
    <META http-equiv="refresh" content="0;URL=/BaltradDex">
  </HEAD>
  <BODY>
  </BODY>
</HTML>
    """)
    fp.close()
  
  ##
  # Installs a patched version of server.xml
  # @param patchdir: the name of the directory where the patch file resides. Path will be thisdir/../patches/<patchdir>/server.xml.in
  # @param env: the build environment
  #
  #def patch_server_xml(self, patchdir, portstr, troot, installerroot):
  def patch_server_xml(self, patchdir, env):
    portstr = env.getArg("TOMCATPORT")
    secureportstr = env.getArg("TOMCATSECUREPORT")
    keystorefile = env.expandArgs("$KEYSTORE/keystore.jks")
    keystorepwd = ""
    if env.hasArg("KEYSTORE_PWD"):
      keystorepwd = env.getArg("KEYSTORE_PWD")
    troot = env.expandArgs("$TPREFIX/tomcat")
    installerroot = env.getInstallerPath()
      
    ifp = open("%s/patches/%s/server.xml.in"%(installerroot, patchdir), "r")
    ofp = open("%s/conf/server.xml"%troot, "w")
    inlines = ifp.readlines()
    for l in inlines:
      tl = l
      if tl.find("CFG_TOMCATPORT") >= 0:
        tl = tl.replace("CFG_TOMCATPORT", portstr)
      if tl.find("<!--WITH_SECURE_COMMUNICATION_BEG") >= 0:
        idx = tl.find("<!--WITH_SECURE_COMMUNICATION_BEG")
        tl = " "*idx
        tl = tl + "<!--WITH_SECURE_COMMUNICATION_BEG-->\n"
      if tl.find("WITH_SECURE_COMMUNICATION_END-->") >= 0:
        idx = tl.find("WITH_SECURE_COMMUNICATION_END-->")
        tl = " "*idx
        tl = tl + "<!--WITH_SECURE_COMMUNICATION_END-->\n"
      if tl.find("CFG_TOMCATSECUREPORT") >= 0:
        tl = tl.replace("CFG_TOMCATSECUREPORT", secureportstr)
      if tl.find("CFG_KEYSTORE_JKS_FILE") >= 0:
        tl = tl.replace("CFG_KEYSTORE_JKS_FILE", keystorefile)
      if tl.find("CFG_KEYSTOREPWD") >= 0:
        tl = tl.replace("CFG_KEYSTOREPWD", keystorepwd)

      ofp.write(tl)
    ifp.close()
    ofp.close()

  ##
  # Patches catalina.sh to include options for higher memory options
  # @param patchdir: the directory of the tomcat that should be patched
  # @param env: the build environment
  def patch_catalina_sh(self, patchdir, env):
    cdir = os.getcwd()
    
    try:
      os.chdir(patchdir)
      code = subprocess.call("patch -p0 < %s/patches/%s/catalina-sh_memory_opts.patch"%(env.getInstallerPath(), patchdir), shell=True)
      if code != 0:
        raise InstallerException, "Failed to apply catalina patch %s/catalina-sh_memory_opts.patch"%patchdir
    finally:
      os.chdir(cdir)


