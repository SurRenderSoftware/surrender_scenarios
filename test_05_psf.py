#! python3
# -*- coding: utf-8 -*-
"""
 SurRender
 Script : SCR_05 PSF
 (C) 2019 Airbus copyright all rights reserved
"""
import os
import sys
from surrender.surrender_client import surrender_client
import numpy as np
import matplotlib.pyplot as plot
from PIL import Image
try:
    from surrender_test.util import config, with_pytest, s, script_dir
except Exception as e:
    print(e)

#--[CONSTANTS]---------------------------
SUN_RADIUS          =    696342000.0 #m
EARTH_SUN_DISTANCE  = 149597870000.0 #m
JUPITER_SUN_DISTANCE= 778412027000.0 #m

#-----------------------------------------------------------------------
"""
This function extracts a (2<dx>+1)X(2<dy>+1) subimage of <im>
centered at <x>,<y>
This result if writen in the console, in a text file <file>.txt an plot
in an image file <file>.tif
Parameters:
im  : the image
col : (x,dx) : the X-center of the extract and the half size
lin : (y,dy) : the Y-center of the extract and the half size
file: the filename of the result without extension
"""
def extractSceneIM(im,lin,col,file):
  # Controls
  x,dx=col
  y,dy=lin
  if x-dx<0 or y-dy<0 or x+dx>im.shape[0] or y+dy>im.shape[1]: return

  # Extract
  imExtr=im[y-dy:y+dy+1]
  imExtr=np.transpose(imExtr)
  imExtr=imExtr[x-dx:x+dx+1]
  imExtr=np.transpose(imExtr)

  # Console and text file
  f=open("%s.txt"%file,'a')
  print("Extract :")
  f.write("Extract :\n")
  for iy in range(2*dy+1):
    print("  line %3d :"%(y-dy+iy),end=" ")
    f.write("  line %3d :"%(y-dy+iy))
    for ix in range(2*dx+1):
      if iy==dy and ix==dx:
        print("[%1.8f] "%imExtr[iy][ix],end=" ")
        f.write("[%1.8f] "%imExtr[iy][ix])
      else:
        print(" %1.8f  "%imExtr[iy][ix],end=" ")
        f.write(" %1.8f  "%imExtr[iy][ix])
    print("")
    f.write("\n")
  f.close()

  # Plot in an image file
  plot.ioff()
  fig=plot.imshow(imExtr, interpolation = "none", cmap = 'hot')
  plot.colorbar(fig)
  plot.savefig("%s.png"%file)
  plot.clf()


#-----------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------
def test_render(with_pytest: bool, config, s, script_dir):

  #--[Connection to server]--------------------------------
  if not with_pytest:
    s = surrender_client()
  s.setVerbosityLevel(1)
  s.connectToServer("127.0.0.1", 5151)

  print("----------------------------------------")
  print("SCRIPT : %s"%sys.argv[0])
  print("SurRender version: "+s.version())
  print("----------------------------------------")

  for PSFsize in [0,3,5,7]:

    print("----------------------------------------")
    print("Running PSF test with size = ", PSFsize)


    #--[PSF definition]---------------------
    psf = np.array(range(PSFsize))-int(PSFsize/2)
    psf = np.meshgrid(psf,psf)
    psf = np.exp(-(psf[0]*psf[0] + psf[1]*psf[1]) / 2.)
    psf = psf / np.sum(psf)

    #--[Initialisation]--------------------------
    s.reset()
    s.closeViewer()
    s.setConventions(s.XYZ_SCALAR_CONVENTION,s.Z_FRONTWARD)
    s.enableDoublePrecisionMode( True )
    s.enableRaytracing(True)
    s.setNbSamplesPerPixel(1024)
    s.enableRegularPixelSampling(True)
    s.enableDoublePrecisionMode(True)
    s.setTimeOut(3600)

    #--[Objects creation]---------------------
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
    xCamPos = JUPITER_SUN_DISTANCE
    yCamPos = 0
    zCamPos = 0
    s.setObjectPosition("camera", (xCamPos,yCamPos,zCamPos))

    # Camera attitude
    u = np.array([0,1,0])
    angle = -np.pi/2
    axis = u/np.linalg.norm(u) * np.sin(angle/2)
    quaternion = np.array( axis.tolist() + [np.cos(angle/2)])
    s.setObjectAttitude("camera", quaternion)

    #--[FOV configuration]------------------------
    xFOV = 40 #deg
    yFOV = 40 #deg
    s.setCameraFOVDeg(xFOV,yFOV)

    #--[Image size]------------------------
    imageSize=511
    s.setImageSize(imageSize,imageSize)

    #--[PSF creation]---------------------
    lin,col=psf.shape
    dist=int(max(lin,col)/2)+2
    s.setPSF(psf,lin,col)
    s.enableRegularPSFSampling(True)

    #--[Rendering]------------------------
    s.render()

    #--[Image recovery]------------------------
    image = s.getImageGray32F()
    im=Image.fromarray(image)
    if with_pytest:
      from surrender_test.check import check_img_error_hist
      check_img_error_hist(config, image, f"{script_dir}/../../surrender-nonreg-test/user_manual/control/SCR05_ref_{PSFsize}.tif")
    else:
      im.save(os.path.join('SCR05_image_%d.tif'%PSFsize))

      xCenter=int((imageSize-1)/2)
      yCenter=int((imageSize-1)/2)
      extractSceneIM(s.getImageGray32F(),(yCenter,dist),(xCenter,dist),'SCR05_extract_%d'%PSFsize)

  print("SCR_05: done.")
  print("----------------------------------------")

if __name__ == "__main__":
    test_render(False, None, None, None)
#-----------------------------------------------------------------------
# End
