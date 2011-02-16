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

Validates the psql

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-08
'''
from ValidatorException import ValidatorException
import subprocess, os
import re, platform

##
# PSQL Validator, tests if the provided psql library provides sufficient support
#
class psqlvalidator:
  ##
  # Default constructor
  def __init__(self):
    pass
  
  ##
  # Removes the list of files
  # @param files. a list of files
  #
  def _remove_files(self, files):
    for f in files:
      try:
        os.unlink(f)
      except:
        pass
  
  ##
  # Verifies that the provided zlib is usable.
  # @param env: the build environment
  # @param zlibinc: the include directory
  # @param zliblib: the lib directory
  #
  def _test_compile_testprog(self, env):
    self._remove_files(["testpsql.c", "testpsql"])
    
    psqlinc = None
    psqllib = None
    dbuser = env.getArg("DBUSER")
    dbpwd = env.getArg("DBPWD")
    dbname = env.getArg("DBNAME")
    dbhost = env.getArg("DBHOST")
    
    if env.hasArg("PSQLINC"):
      psqlinc = env.getArg("PSQLINC")
    if env.hasArg("PSQLLIB"):
      psqllib = env.getArg("PSQLLIB")
      
    #./testconn "user=$DBUSER password=$DBPWD dbname=$DBNAME hostaddr=$DBHOST"
    
    progstr="""
#include <stdio.h>
#include "libpq-fe.h"

extern void exit(int);

int main(int argc, char** argv) {
  PGconn* connection = NULL;
  int serverversion = 0;

  if (argc != 2) {
    fprintf(stderr, "Usage: %s <pq connect string>\\n", argv[0]);
    fprintf(stderr, "e.g. %s \\"user=baltrad password=xyz dbname=baltrad hostaddr=127.0.0.1\\"\\n", argv[0]);
    exit(255);
  }

  connection = PQconnectdb(argv[1]);
  if (PQstatus(connection) != CONNECTION_OK) {
    fprintf(stderr, "Failed to connect to database: %s\\n",PQerrorMessage(connection));
    PQfinish(connection);
    exit(255);
  }  

  serverversion = PQserverVersion(connection);

  PQfinish(connection);

  if (serverversion < 80309) {
    fprintf(stderr, "Postgres server is of version %d but must be >= 8.3.9\\n", serverversion);
    exit(255);
  }

  fprintf(stderr, "Connected & version >= 8.3.9\\n");
  exit(0);
  return 0;
}
"""
    fp = open("testpsql.c", "w")
    fp.write(progstr)
    fp.close()
    
    cmd = "gcc"
    if psqlinc != None and psqlinc != "":
      cmd = "%s -I%s"%(cmd,psqlinc)
    
    if psqllib != None and psqllib != "":
      cmd = "%s -L%s"%(cmd,psqllib)
    
    cmd = "%s -o testpsql testpsql.c -lpq"%cmd

    code = subprocess.call(cmd, shell=True)
    if code != 0:
      #self._remove_files(["testpsql.c", "testpsql"])
      raise ValidatorException, "Failed to compile psql test program"
    
    cmd = "./testpsql \"user=%s password=%s dbname=%s hostaddr=%s\""%(dbuser,dbpwd,dbname,dbhost)
    if psqllib != None and psqllib != "":
      cmd = "LD_LIBRARY_PATH=%s %s"%(psqllib, cmd)

    code = subprocess.call(cmd, shell=True)
    if code != 0:
      #self._remove_files(["testpsql.c", "testpsql"])
      raise ValidatorException, "Failed to run psql test program, have you got a dbversion >= 8.3.9 and specified correct db arguments"

    self._remove_files(["testpsql.c", "testpsql"])
    
  ##
  # Performs the actual validation of a jdk
  # @param env: the build environment
  #
  def validate(self, env):
    self._test_compile_testprog(env)
    print "PSQL tested ok"

