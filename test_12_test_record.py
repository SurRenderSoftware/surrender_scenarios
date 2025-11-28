#! python3
# -*- coding: utf-8 -*-
"""
 SurRender script
 Script : 
 (C) 2023 Airbus copyright all rights reserved
 # Test for record a script for debug
"""

import sys
from surrender.surrender_client import surrender_client
import numpy as np
from PIL import Image
try:
    from surrender_test.util import config, with_pytest, s, script_dir
except Exception as e:
    print(e)


#--[CONSTANTS]---------------------------
SUN_RADIUS         =    696342000.0 #m
EARTH_RADIUS       =      6478137.0 #m
EARTH_SUN_DISTANCE = 149597870000.0 #m

#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------

def test_render(with_pytest: bool, config, s, script_dir):

  #--[Connection to server]--------------------------------
  if not with_pytest:
      s = surrender_client()
  s.setVerbosityLevel(1)
  s.connectToServer("127.0.0.1", 5151)
  s.record()


  print("----------------------------------------")
  print("SCRIPT : %s"%sys.argv[0])
  print("SurRender version: "+s.version())
  print("----------------------------------------")

  #--[Initialisation]--------------------------
  s.closeViewer()
  s.setConventions(s.XYZ_SCALAR_CONVENTION,s.Z_FRONTWARD)
  s.enableDoublePrecisionMode( True )
  s.enableRaytracing( True )
  s.setNbSamplesPerPixel(1)

  #--[Objects creation]---------------------
  # Earth
  s.createBRDF("mate",   "mate.brdf",   {})
  s.createShape("earth_shape", "sphere.shp", {'radius': EARTH_RADIUS})
  s.createBody("earth", "earth_shape", "mate", ["earth.jpg"])

  # Earth position
  xEarthPos = 0
  yEarthPos = 0
  zEarthPos = -(EARTH_RADIUS + 2*np.power(10,7))
  s.setObjectPosition("earth", (xEarthPos, yEarthPos, zEarthPos))

  # Sun
  s.createBRDF("sun",    "sun.brdf",    {})
  s.createShape("sun_shape", "sphere.shp", {'radius':SUN_RADIUS})
  s.createBody("sun", "sun_shape", "sun", [])

  # Sun position
  xSunPos = 0
  ySunPos = 0
  zSunPos = EARTH_SUN_DISTANCE-zEarthPos
  s.setObjectPosition("sun", (xSunPos, ySunPos, zSunPos))

  # Sun illumination
  p = EARTH_SUN_DISTANCE * EARTH_SUN_DISTANCE * np.pi
  s.setSunPower(np.array([p,p,p,p]))

  #--[Camera position]-----------------------
  xCamPos = 0
  yCamPos = 0
  zCamPos = 0
  s.setObjectPosition( "camera", (xCamPos, yCamPos, zCamPos ))

  #--[Image size (4/3)]------------------------
  imWidth  = 640
  imHeight = 480
  s.setImageSize(imWidth, imHeight)

  #--[FOV configuration (4/3)]------------------------
  xFOV = 40.0 #deg
  yFOV = 30.0 #deg
  s.setCameraFOVDeg(xFOV, yFOV)

  #--[Rendering]------------------------
  s.render()

  #--[Image recovery]------------------------

  # Gray
  image = s.getImageGray8()
  Image.fromarray(image).save('SCR12_imageGray.png')

  # Color
  imageRGBA = s.getImageRGBA8()
  Image.fromarray(imageRGBA).save('SCR12_imageRGBA.png')

  with open("my_record.py", "w") as log_file:
      print(s.generateReplay(), file=log_file)
      print("def my_img():\n  return s.getImageRGBA8()", file=log_file)

  if with_pytest:
      from surrender_test.check import check_img_error_hist
      from my_record import my_img
      check_img_error_hist(config, my_img()[...,:3], f"{script_dir}/../../surrender-nonreg-test/user_manual/control/SCR12_ref.png")
      check_img_error_hist(config, imageRGBA[...,:3], f"{script_dir}/../../surrender-nonreg-test/user_manual/control/SCR12_ref.png")
  else:
      # get rid of the alpha channel
      r,g,b,a = Image.fromarray(imageRGBA).split()
      imageRGB = Image.merge("RGB", (r, g, b))
      imageRGB.save('SCR12_imageRGB.png')

  print("Process done.")
  print("----------------------------------------")

if __name__ == "__main__":
    test_render(False, None, None, None)
#-----------------------------------------------------------------------
# End
