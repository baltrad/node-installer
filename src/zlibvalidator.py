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

Validates the zlib and provided paths

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-08
'''
from ValidatorException import ValidatorException
import subprocess, os
import re, platform

##
# ZLIB Validator, tests if the external zlib provides sufficient support
#
class zlibvalidator:
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
  def _test_compile_testprog(self, env, zlibinc, zliblib):
    self._remove_files(["testzlib.c", "testzlib"])
    
    progstr="""
#include <stdio.h>
#include "zlib.h"
#include <stdlib.h>
int main(int argc, char** argv) {
  while (0) {
    compress2(NULL, NULL, NULL, 0, 0);
  }
  exit(0);
  return 0;
}
"""
    fp = open("testzlib.c", "w")
    fp.write(progstr)
    fp.close()
    
    cmd = "gcc"
    if zlibinc != None and zlibinc != "":
      cmd = "%s -I%s"%(cmd,zlibinc)
    
    if zliblib != None and zliblib != "":
      cmd = "%s -L%s"%(cmd,zliblib)
    
    cmd = "%s -o testzlib testzlib.c -lz"%cmd

    code = subprocess.call(cmd, shell=True)
    if code != 0:
      self._remove_files(["testzlib.c", "testzlib"])
      raise ValidatorException, "Failed to compile zlib test program"
    
    cmd = "./testzlib"
    if zliblib != None and zliblib != "":
      cmd = "LD_LIBRARY_PATH=%s %s"%(zliblib, cmd)

    code = subprocess.call(cmd, shell=True)
    if code != 0:
      self._remove_files(["testzlib.c", "testzlib"])
      raise ValidatorException, "Failed to run zlib test program"

    self._remove_files(["testzlib.c", "testzlib"])
    
  ##
  # Performs the actual validation of a jdk
  # @param env: the build environment
  #
  def validate(self, env):
    if env.isExcluded("ZLIB"):
      if env.hasArg("ZLIBINC"):
        zlibinc = env.getArg("ZLIBINC")
      if env.hasArg("ZLIBLIB"):
        zliblib = env.getArg("ZLIBLIB")
      self._test_compile_testprog(env, zlibinc, zliblib)
      print "External ZLIB tested ok"

