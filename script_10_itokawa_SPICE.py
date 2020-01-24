#! python3
# -*- coding: utf-8 -*-
"""
 SurRender script
 Script : SCR_10 Simulate Itokawa images taken from the PDS with SPICE data
"""
from surrender.surrender_client import surrender_client
from surrender.geometry import vec3, vec4, quat, normalize, QuatToMat, MatToQuat, gaussian
import numpy as np
import os
import spiceypy 
import cv2
from PIL import Image
import matplotlib.pyplot as plot
import ntpath
import urllib.request
from bs4 import BeautifulSoup
import sys
import errno
from astropy.io import fits

def getKernels(p, d, e):
	base = os.path.join(p, d)
	return [os.path.join(base, f) for f in os.listdir(base) if f.endswith(e)]


def getImageTime(file):
	with open(file, 'r') as f:
		lines = f.readlines()
	startTimeLine = [l for l in lines if l.startswith('START_TIME')][0]
	return startTimeLine.split('=')[-1].strip()
    
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# Directory where to store images and kernels
imagesDir = "imagesItokawaPDS"
spiceDir = "dataSPICE"
outputDir = "imagesItokawaPDS_SurRender"
pathScript = os.path.dirname(os.path.abspath(__file__))
imagesDir = os.path.join(pathScript,imagesDir)
spiceDir = os.path.join(pathScript,spiceDir)
outputDir = os.path.join(pathScript,outputDir)
mkdir_p(imagesDir)
mkdir_p(spiceDir)
mkdir_p(outputDir)

# URL of the SPICE and PDS data 
URL_images ='https://sbnarchive.psi.edu/pds3/hayabusa/HAY_A_AMICA_3_HAYAMICA_V1_0/data/20051001/'
source = 'naif.jpl.nasa.gov/pub/naif/pds/data/hay-a-spice-6-v1.0/haysp_1000/data/'
URL_dataSPICE = 'ftp://' + source

# Download SPICE data with wget. This command requires 10 minutes comment it if you have already the SPICE kernels 
cmdToExecute = 'wget -r --no-parent --reject "index.html*" ' + URL_dataSPICE +' -P ' + spiceDir
os.system(cmdToExecute)

# Download PDS data
# We decided to plot only "v" (green) images (see Ishiguro, Masateru, et al. 
# "The hayabusa spacecraft asteroid multi-band imaging camera (AMICA)." Icarus 207.2 (2010): 714-731. 
# for nomenclature)
urlpath =urllib.request.urlopen(URL_images)
soup = BeautifulSoup(urlpath.read(), "lxml")
filterAMICA = "_v"
for element in soup.findAll('a'):
	if filterAMICA in element.get('href'):
		urllib.request.urlretrieve(URL_images+element.get('href'), os.path.join(imagesDir,element.get('href')))
		print("Downloaded: " + element.get('href'))

spiceDir = os.path.join(spiceDir, source)

kFiles = getKernels(spiceDir, 'ck', '.bc')
kFiles += getKernels(spiceDir, 'fk', '.tf')
kFiles += getKernels(spiceDir, 'ik', '.ti')
kFiles += getKernels(spiceDir, 'lsk', '.tls')
kFiles += getKernels(spiceDir, 'pck', '.tpc')
kFiles += getKernels(spiceDir, 'lsk', '.tls')
kFiles += getKernels(spiceDir, 'sclk', '.tsc')
kFiles += getKernels(spiceDir, 'spk', '.bsp')
spiceypy.furnsh(kFiles)

iFiles = [os.path.join(imagesDir,f) for f in os.listdir(imagesDir) if f.endswith(filterAMICA + '.lbl')]

# Constants:
sun_radius = 696342000
ua2km = 149597870.700
ua = ua2km * 1000
pi = np.pi

# Image setup:
fov=5.8
raytracing=True
ImageSize = [1024 , 1024]

# set PSF
surech_PSF=10
sigma = 1
wPSF = 5
PSF = gaussian(wPSF * surech_PSF, sigma * surech_PSF)

## Initializing SurRender
s = surrender_client()
s.setVerbosityLevel(1)
s.connectToServer('127.0.0.1')
s.setCompressionLevel(0);
s.closeViewer()
s.setTimeOut(86400)

s.setShadowMapSize(512)
s.setCubeMapSize(512)
s.enableMultilateralFiltering(False)
s.enablePreviewMode(True)
s.enableDoublePrecisionMode(False)
s.enableRaytracing(True)

s.setConventions(s.SCALAR_XYZ_CONVENTION,s.Z_FRONTWARD);
s.setPSF(PSF,wPSF,wPSF)

if raytracing:
    s.enableFastPSFMode(False)
    s.enableRaytracing(True)
    s.enableIrradianceMode(False)
    s.setNbSamplesPerPixel(16) # Raytracing
    s.enableRegularPSFSampling(True)
    s.enablePathTracing(False)
else:
    s.enableFastPSFMode(True)
    s.enableRaytracing(False)
    s.enableIrradianceMode(False)
    s.enablePathTracing(False)


s.createBRDF('sun_BRDF', 'sun.brdf', {})
s.createShape('sun_shape', 'sphere.shp', { 'radius' : sun_radius })
s.createBody('sun', 'sun_shape', 'sun_BRDF', [])
s.setSunPower(8*ua*ua*pi*5.2*5.2*vec4(1,1,1,1))

s.createBRDF('hapke', 'hapke.brdf', {})
s.createMesh('asteroid', 'itokawa.obj', 1e3)
s.setObjectElementBRDF('asteroid', 'asteroid', 'hapke')

s.setCameraFOVDeg(fov, np.arctan(np.tan(fov/360*pi)*ImageSize[1]/ImageSize[0])*360/pi)
s.setImageSize(ImageSize[0],ImageSize[1])


fig=plot.figure()
for p in iFiles:
	
	# getting positions and quaternion in the camera frame
	et1Str = getImageTime(p)
	target = 'HAYABUSA'
	et1 = spiceypy.utc2et(et1Str)
	frame = 'ITOKAWA_FIXED'
	center = 'ITOKAWA'
	state1 = spiceypy.spkezr(target, spiceypy.utc2et(et1Str), frame, 'none', center)[0]
	stateSun = spiceypy.spkezr('SUN', spiceypy.utc2et(et1Str), frame, 'none', center)[0]
	frame2 = 'HAYABUSA_AMICA'
	frame1 = 'ITOKAWA_FIXED'
	rot1 = spiceypy.pxform(frame1, frame2, et1)
	quat1 = spiceypy.m2q(rot1)

	# SPICE data are in km
	s.setObjectPosition('camera', vec3(state1[0]*1000,state1[1]*1000,state1[2]*1000));

	# opposite convetion is used between SurRender and JPL
	s.setObjectAttitude('camera', vec4(quat1[0],-quat1[1],-quat1[2],-quat1[3]));

	# SPICE data are in km
	s.setObjectPosition('sun', vec3(stateSun[0]*1000,stateSun[1]*1000,stateSun[2]*1000));
	s.setObjectPosition('asteroid', vec3(0,0,0));
	s.printState(s.getState())
	s.render();	
	im = s.getImageGray32F();
	imgName = os.path.splitext(ntpath.basename(p))[0] + '.png'
	cv2.imwrite(os.path.join(outputDir,imgName),np.array(np.clip(im * (255 / np.max(im)), 0, 255), dtype=np.uint8))
	
	image_file = os.path.splitext(p)[0] + '.fit'
	image_data = fits.getdata(image_file, ext=0)
	
	fig.add_subplot(1, 2, 1)
	plot.imshow(im, aspect='equal', interpolation='none', cmap='gray');
	fig.add_subplot(1, 2, 2)
	plot.imshow(image_data,  aspect='equal', interpolation='none', cmap='gray');
	plot.draw()
	plot.pause(0.5)   
	
print(' End of simulation')
