#! python3
# -*- coding: utf-8 -*-
"""
 SurRender script
 Script : SCR_02 Simple Earth-Sun-Camera system
 (C) 2019 Airbus copyright all rights reserved
"""
import sys
from surrender.surrender_client import surrender_client
import numpy as np
from PIL import Image

#--[CONSTANTS]---------------------------
SUN_RADIUS         =    696342000.0 #m
EARTH_RADIUS       =      6478137.0 #m
EARTH_SUN_DISTANCE = 149597870000.0 #m

#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------
if __name__ == "__main__":

  #--[Connection to server]--------------------------------
  s = surrender_client()
  s.setVerbosityLevel(1)
  s.connectToServer("127.0.0.1", 5151)

  print("----------------------------------------")
  print("SCRIPT : %s"%sys.argv[0])
  print("SurRender version: "+s.version())
  print("----------------------------------------")

  #--[Initialisation]--------------------------
  s.closeViewer()
  s.setConventions(s.XYZ_SCALAR_CONVENTION,s.Z_FRONTWARD)
  s.enableDoublePrecisionMode( True )
  s.enableRaytracing( True )

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
  s.setObjectPosition( "camera", ( xCamPos, yCamPos, zCamPos ) )

  #--[Image size (4/3)]------------------------
  imWidth  = 640
  imHeight = 480
  s.setImageSize(imWidth, imHeight)

  #--[FOV configuration (4/3)]------------------------
  xFOV = 40.0 #deg
  yFOV = 30.0 #deg
  s.setCameraFOVDeg(xFOV,yFOV)

  #--[Rendering]------------------------
  s.render()

  #--[Image recovery]------------------------

  # Gray
  image = s.getImageGray8()
  Image.fromarray(image).save('SCR02_imageGray.png')

  # Color
  imageRGBA = s.getImageRGBA8()
  Image.fromarray(imageRGBA).save('SCR02_imageRGBA.png')

  # get rid of the alpha channel
  r,g,b,a = Image.fromarray(imageRGBA).split()
  imageRGB = Image.merge("RGB", (r, g, b))
  imageRGB.save('SCR02_imageRGB.png')

  print("SCR_02: done.")
  print("----------------------------------------")

#-----------------------------------------------------------------------
# End
