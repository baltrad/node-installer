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

import os, sys
import shutil
import time
import subprocess

from installer import installer
from InstallerException import InstallerException

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
    
  def _keytool(self, python, *module_args):
    args = [python, "-m", "keyczar.keyczart"]
    args.extend(module_args)
    ocode = subprocess.call(args)
    if ocode != 0:
        raise InstallerException, "keytool command failed"
    
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

    nodekey_pub = env.expandArgs("$KEYSTORE/$NODENAME.pub")
    if not os.path.exists(nodekey_pub):
      print "exporting public key to", nodekey_pub
      self._createdir(nodekey_pub)
      self._keytool(python, "pubkey",
        "--location=%s" % nodekey_priv,
        "--destination=%s" % nodekey_pub
      )

    # Here we maybe should modify permissions of the private key file but for now let it be.
