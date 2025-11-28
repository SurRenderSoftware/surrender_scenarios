#! python3
# -*- coding: utf-8 -*-
"""
 (C) 2019 Airbus copyright all rights reserved
 SurRender
 Script : SCR_00 Installation control
"""
import sys
from surrender.surrender_client import surrender_client

#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------
def test_install():

  #--[Connection to server]--------------------------------
  s = surrender_client()
  s.setVerbosityLevel(1)
  s.connectToServer("127.0.0.1", 5151)

  print("----------------------------------------")
  print("SCRIPT : %s"%sys.argv[0])
  print("SurRender client is connected? %s"% (s.isConnected() > 0) )
  assert(s.isConnected() > 0)
  print("SurRender version: " + s.version() )
  print("SurRender resource path set to: '" + s.getRessourcePath() + "'")
  print("SCR_00: done.")
  print("----------------------------------------")


if __name__ == "__main__":
    test_install()
#-----------------------------------------------------------------------
# End
