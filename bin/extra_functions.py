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

Extra functions that are needed when building the software, probably
argument generation functions or other misc functions.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-02
'''

def zlib_optional_arg(benv):
  import platform
  if platform.machine() == 'x86_64':
    return "--64"
  return None

##
# Generates a --with-zlib=<inc>,<lib> argument to be used by hdf5 installed.
# --with-zlib=\"$ZLIBINC\",\"$ZLIBLIB\"
# @param benv: the build environment
# @return: the hdf5 --with-zlib argument or None
#
def hdf5_optional_zlib_arg(benv):
  inc = None
  lib = None
  result = None
  if benv.hasArg("ZLIBINC"):
    inc = benv.getArg("ZLIBINC")
  if benv.hasArg("ZLIBLIB"):
    lib = benv.getArg("ZLIBLIB")
  
  if inc != None or lib != None:
    result = "--with-zlib="
    if inc != None:
      result = result + inc
    result = result + ","
    if lib != None:
      result = result + lib
      
  return result
