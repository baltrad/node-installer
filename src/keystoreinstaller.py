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

import os, sys, stat
import shutil
import time
import subprocess

from installer import installer
from InstallerException import InstallerException

##
# Function that performs chmod. Called by a walker
# @param mode: the mode
# @param dirname: name of directory
# @param fnames: the filenames in the directory
#
def _walk_chmod(mode, dirname, fnames):
  os.chmod(dirname, mode | stat.S_IXUSR)
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
# Keystore installer
#
class keystoreinstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(keystoreinstaller, self).__init__(package, None)
    
  ##
  # Checks if the provided dir exists and if not creates it
  # @param dir: the dir name
  def _createdir(self, dir):
    if not os.path.exists(dir):
      os.mkdir(dir)
    elif not os.path.isdir(dir):
      raise InstallerException, "%s exists but is not a directory"%dir
  
  ##
  # Sets permissions on the private key so that it only is
  # user that is able to read it.
  # @param env: the build environment
  # @param dir: the directory where the key resides
  #
  def _setup_permissions(self, env, dir):
    import getpass, pwd, sys
    runas = env.getArg("RUNASUSER")
    if runas == "root":
      raise InstallerException, "You should not atempt to run system as root"

    obj = pwd.getpwnam(runas)

    if runas == getpass.getuser() or "root" == getpass.getuser():
      if "root" == getpass.getuser():
        os.path.walk(dir, _walk_chown, [obj.pw_uid,obj.pw_gid])
      os.path.walk(dir, _walk_chmod, stat.S_IRUSR|stat.S_IWUSR)
    else:
      print "Can not set proper permissions on private key"
      print env.expandArgs(""" Please modify permissions accordingly before continuing...
chown -R $RUNASUSER:$RUNASUSER %s
chmod -R 600 %s
"""%(dir,dir))
      print "Press return when finished or write 'quit' to exit:",
      sys.stdout.flush()
      a=sys.stdin.readline().strip()
      if a == "quit":
        raise InstallerException, "Manually terminated script"

  ##
  # Runs the keytool
  #   
  def _keytool(self, python, *module_args):
    args = [python, "-m", "keyczar.keyczart"]
    args.extend(module_args)
    ocode = subprocess.call(args)
    if ocode != 0:
        raise InstallerException, "keytool command failed"
  
  #self._create_keystore(env, keystore_pth)
  def _create_keystore(self, env, keystore_pth):
    #$JAVA_HOME/bin/keytool -genkey -alias tomcat -keyalg RSA -validity 3650 -keystore /opt/baltrad/etc/bltnode-keys/keystore.jks
    keytool = env.expandArgs("$JDKHOME/bin/keytool")
    
    kpwd = env.getArg("KEYSTORE_PWD")
    
    if not os.path.exists(keytool):
      raise InstallerException, "Could not locate keytool command"
    args = [keytool, "-genkey", "-alias", "tomcat", "-keyalg", "RSA", "-validity", "3650", "-keypass", kpwd, "-storepass", kpwd, "-keystore", keystore_pth]
    if env.hasArg("KEYSTORE_DN"):
      dn = env.getArg("KEYSTORE_DN")
      if dn == "yes":
        dn = None
      elif dn == "no":
        dn = "CN=Unknown,OU=Unknown,O=Unknown,L=Unknown,ST=Unknown,C=Unknown"
      if dn != None:
        args.extend(["-dname", dn])

    ocode = subprocess.call(args)
    if ocode != 0:
      raise InstallerException, "keytool command failed for keystore creation"
    
    #/usr/bin/keytool -genkey -noprompt -alias tomcat -keyalg RSA -validity 3650 -keypass smurfen -storepass smurfen -dname "CN=Unknown, OU=Unknown, O=Unknown, L=Unknown, ST=Unknown, C=Unknown" -keystore /tmp/slask.jks
    
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    self._createdir(env.expandArgs("$PREFIX/etc"))
    keystore = env.expandArgs("$KEYSTORE")
    if not os.path.exists(keystore):
      self._createdir(keystore)

    python = env.expandArgs("${TPREFIX}/bin/python")

    nodekey_priv = env.expandArgs("$KEYSTORE/$NODENAME.priv")
    if not os.path.exists(nodekey_priv):
      print "creating private key in", nodekey_priv
      self._createdir(nodekey_priv)
      self._keytool(python, "create",
        "--location=%s" % nodekey_priv,
        "--purpose=sign",
        "--name=%s" % env.expandArgs("$NODENAME"),
        "--asymmetric=dsa"
      )
      self._keytool(python, "addkey",
        "--location=%s" % nodekey_priv,
        "--status=primary"
      )
      self._setup_permissions(env, nodekey_priv)

    nodekey_pub = env.expandArgs("$KEYSTORE/$NODENAME.pub")
    if not os.path.exists(nodekey_pub):
      print "exporting public key to", nodekey_pub
      self._createdir(nodekey_pub)
      self._keytool(python, "pubkey",
        "--location=%s" % nodekey_priv,
        "--destination=%s" % nodekey_pub
      )

    if env.hasArg("KEYSTORE_PWD"): # We only create the keystore if we have keystorepwd
      keystore_pth = env.expandArgs("$KEYSTORE/keystore.jks")
      if not os.path.exists(keystore_pth):
        print "creating keystore file", keystore_pth
        self._create_keystore(env, keystore_pth)
      
    # Here we maybe should modify permissions of the private key file but for now let it be.
