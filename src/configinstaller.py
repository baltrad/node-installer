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
import urllib

from installer import installer
from InstallerException import InstallerException

class configinstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(configinstaller, self).__init__(package, None)
    
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
    self._createdir(env.expandArgs("$PREFIX/etc"))

    dst = env.expandArgs("$PREFIX/etc/bltnode.properties")
    backup = dst + "%s.bak" % time.strftime("%Y%m%dT%H%M%S")
    if os.path.exists(dst):
        shutil.move(dst, backup)
    
    env.addArg("BDB_ENCODED_DBPWD", urllib.quote_plus(env.getArg("DBPWD")))
    conf = [
      "baltrad.bdb.server.type = werkzeug",
      "baltrad.bdb.server.uri = http://localhost:$BDB_PORT",
      "baltrad.bdb.server.backend.type = sqla",
      "baltrad.bdb.server.backend.sqla.uri = postgresql://$DBUSER:$BDB_ENCODED_DBPWD@$DBHOST/$DBNAME",
      "baltrad.bdb.server.backend.sqla.pool_size = $BDB_POOL_MAX_SIZE",
      "baltrad.bdb.server.backend.sqla.storage.type=db",
    ]
    auth = env.getArg("BDB_AUTH")
    if auth == "keyczar":
      conf.extend([
        "baltrad.bdb.server.auth.providers=noauth, keyczar",
        "baltrad.bdb.server.auth.keyczar.keystore_root = $KEYSTORE",
        "baltrad.bdb.server.auth.keyczar.keys.$NODENAME = $NODENAME.pub",
      ])
    elif auth == "noauth":
      conf.append("baltrad.bdb.server.auth.providers = noauth")
    else:
      raise InstallerException, "unrecognized BDB_AUTH: %s" % auth

    conf = [env.expandArgs(c) for c in conf]
    outfile = open(dst, "w")
    outfile.write("\n".join(conf))
