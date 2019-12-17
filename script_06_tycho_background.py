#! python3
# -*- coding: utf-8 -*-
"""
 SurRender
 Script : SCR_06 Tycho background
 (C) 2019 Airbus copyright all rights reserved
"""
import os
import sys
from surrender.surrender_client import surrender_client
import numpy as np
from PIL import Image
import matplotlib.pyplot as plot

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
        f.write("[%1.16f] "%imExtr[iy][ix])
      else:
        print(" %1.8f  "%imExtr[iy][ix],end=" ")
        f.write(" %1.16f  "%imExtr[iy][ix])
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
if __name__ == "__main__":

  #--[Connection to server]--------------------------------
  s = surrender_client()
  s.setVerbosityLevel(1)
  s.connectToServer("127.0.0.1", 5151)

  print("----------------------------------------")
  print("SCRIPT : %s"%sys.argv[0])
  print("SurRender version: "+s.version())
  print("----------------------------------------")

  #--[PSF definition]---------------------
  PSFsize=3
  psf = np.array(range(PSFsize))-int(PSFsize/2)
  psf = np.meshgrid(psf,psf)
  psf = np.exp(-(psf[0]*psf[0] + psf[1]*psf[1]) / 2.)
  psf = psf / np.sum(psf)
  lin,col=psf.shape
  dist=int(max(lin,col)/2)+2

  #--[Initialisation]--------------------------
  s.reset()
  s.closeViewer()
  s.setConventions(s.XYZ_SCALAR_CONVENTION,s.Z_FRONTWARD)
  s.enableRaytracing(True)
  s.setNbSamplesPerPixel(10)
  s.enableRegularPixelSampling(True)
  s.enableDoublePrecisionMode(True)
  s.setTimeOut(3600)

  #--[Camera]-----------------------
  # Camera position
  xCamPos = 0
  yCamPos = 0
  zCamPos = 0
  s.setObjectPosition("camera", (xCamPos,yCamPos,zCamPos))

  #--[FOV configuration]------------------------
  xFOV=5.0 #deg
  yFOV=5.0 #deg
  s.setCameraFOVDeg(xFOV,yFOV)

  #--[Image size]------------------------
  imageSize=511
  s.setImageSize(imageSize,imageSize)

  #--[PSF creation]---------------------
  s.setPSF(psf,lin,col,dist)
  s.enableRegularPSFSampling(True)

  #--[Star map]------------------------
  s.setBackground("tycho-2_V_RGBx.bin")

  #--[Rendering]------------------------
  s.render()

  #--[Image recovery]------------------------
  im=Image.fromarray(s.getImageGray32F())
  enh=im.point(lambda i: i*np.power(10.0,12))
  enh.save(os.path.join('SCR06_tycho-2_V_RGBx.tif'))

  xCenter=299
  yCenter=122
  dist=8
  extractSceneIM(s.getImageGray32F(),(yCenter,dist),(xCenter,dist),'SCR06_tycho-2_V_RGBx_Extract')

  print("SCR_06: done.")
  print("----------------------------------------")

#-----------------------------------------------------------------------
# End
