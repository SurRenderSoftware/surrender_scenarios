#! python3
# -*- coding: utf-8 -*-
"""
 SurRender
 Script : SCR_04 Raytracing precision
 (C) 2019 Airbus copyright all rights reserved
"""
import os
import sys
from surrender.surrender_client import surrender_client
import numpy as np
from PIL import Image
try:
    from surrender_test.util import config, with_pytest, s, script_dir
except Exception as e:
    print(e)

#--[CONSTANTS]---------------------------
EARTH_RADIUS        =      6478137.0 #m
SUN_RADIUS          =    696342000.0 #m
MOON_RADIUS         =      1737100.0 #m
EARTH_SUN_DISTANCE  = 149597870000.0 #m
EARTH_MOON_DISTANCE =    380000000.0 #m


#-----------------------------------------------------------------------
"""
This function performs the multiplication of two quaternions <q1>x<q2>
Parameters:
q1,q2 : the quaternion to multiply
"""
def quatMultiplication(q1,q2):
  x1=q1[0];    x2=q2[0]
  y1=q1[1];    y2=q2[1]
  z1=q1[2];    z2=q2[2]
  w1=q1[3];    w2=q2[3]

  x = w2*x1 + x2*w1 + y2*z1 - z2*y1
  y = w2*y1 - x2*z1 + y2*w1 + z2*x1
  z = w2*z1 + x2*y1 - y2*x1 + z2*w1
  w = w2*w1 - x2*x1 - y2*y1 - z2*z1

  return np.array([x,y,z,w])

#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------
def test_render(with_pytest: bool, config, s, script_dir):

  #--[Connection to server]--------------------------------
  if not with_pytest:
    s = surrender_client()
  s.setVerbosityLevel(1)
  s.connectToServer("127.0.0.1", 5151)
  s._async = False

  print("----------------------------------------")
  print("SCRIPT : %s"%sys.argv[0])
  print("SurRender version: "+s.version())
  print("----------------------------------------")

  #--[Initialisation]--------------------------
  s.closeViewer()
  s.setConventions(s.XYZ_SCALAR_CONVENTION,s.Z_FRONTWARD)
  s.enableDoublePrecisionMode( True )
  s.enableRaytracing(True)
  s.setNbSamplesPerPixel(16)
  s.setTimeOut(3600)

  #--[Objects creation]---------------------
  # Earth
  s.createBRDF("mate",   "mate.brdf",   {})
  s.createShape("earth_shape", "sphere.shp", {'radius': EARTH_RADIUS})
  s.createBody("earth", "earth_shape", "mate", ["earth.jpg"])

  # Earth position
  xEarthPos = EARTH_SUN_DISTANCE
  yEarthPos = 0
  zEarthPos = 0
  s.setObjectPosition("earth", (xEarthPos, yEarthPos, zEarthPos))

  # Earth attitude
  #- first rotation: angle 180° around Z axis
  u = np.array([0,0,1])
  angle = np.pi
  axis = u/np.linalg.norm(u) * np.sin(angle/2)
  quat1 = np.array( axis.tolist() + [np.cos(angle/2)])

  #- second rotation: angle -23.5° around Y axis
  u = np.array([0,1,0])
  angle = -23.5/180*np.pi
  axis = u/np.linalg.norm(u) * np.sin(angle/2)
  quat2 = np.array( axis.tolist() + [np.cos(angle/2)])

  #- combination
  quaternion = quatMultiplication(quat1,quat2)
  s.setObjectAttitude("earth", quaternion)

  # Moon
  s.createShape("moon_shape", "sphere.shp", {'radius': MOON_RADIUS})
  s.createBody("moon", "moon_shape", "mate", ["moon.jpg"])

  # Moon position
  xMoonPos = EARTH_SUN_DISTANCE-EARTH_MOON_DISTANCE
  yMoonPos = 0
  zMoonPos = 0
  s.setObjectPosition("moon", (xMoonPos, yMoonPos, zMoonPos))

  # Sun
  s.createBRDF("sun",    "sun.brdf",    {})
  s.createShape("sun_shape", "sphere.shp", {'radius':SUN_RADIUS})
  s.createBody("sun", "sun_shape", "sun", [])

  # Sun position
  xSunPos = 0
  ySunPos = 0
  zSunPos = 0
  s.setObjectPosition("sun", (xSunPos, ySunPos, zSunPos))

  # Sun illumination
  p = EARTH_SUN_DISTANCE * EARTH_SUN_DISTANCE * np.pi
  s.setSunPower(np.array([p,p,p,p]))

  #--[Camera]-----------------------
  # Camera position
  xCamPos = EARTH_SUN_DISTANCE - EARTH_MOON_DISTANCE + MOON_RADIUS
  yCamPos = 0
  zCamPos = 0
  s.setObjectPosition("camera", (xCamPos,yCamPos,zCamPos))

  # Camera attitude
  #- first rotation: angle 90° around Y axis
  u = np.array([0,1,0])
  angle = np.pi/2
  axis = u/np.linalg.norm(u) * np.sin(angle/2)
  quat1 = np.array( axis.tolist() + [np.cos(angle/2)])

  #- second rotation: angle -90° around X axis
  u = np.array([1,0,0])
  angle = -np.pi/2
  axis = u/np.linalg.norm(u) * np.sin(angle/2)
  quat2 = np.array( axis.tolist() + [np.cos(angle/2)])

  #- combination
  quaternion = quatMultiplication(quat1,quat2)
  s.setObjectAttitude("camera", quaternion)

  #--[FOV configuration]------------------------
  xFOV = 2.0 #deg
  yFOV = 2.0 #deg
  s.setCameraFOVDeg(xFOV,yFOV)

  #--[Rendering]------------------------
  s.render()

  #--[Image recovery]------------------------
  image = s.getImageRGBA8()

  # get rid of the alpha channel
  r,g,b,a = Image.fromarray(image).split()
  imageRGB = Image.merge("RGB", (r, g, b))

  if with_pytest:
      from surrender_test.check import check_img_error_hist
      check_img_error_hist(config, image, f"{script_dir}/../../surrender-nonreg-test/user_manual/control/SCR04_ref.png")
  else:
      imageRGB.save('SCR04_imageRGB.png')

  print("SCR_04: done.")
  print("----------------------------------------")

if __name__ == "__main__":
    test_render(False, None, None, None)
#-----------------------------------------------------------------------
# End
