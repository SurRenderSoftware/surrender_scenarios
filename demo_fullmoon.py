#! python3
# -*- coding: utf-8 -*-
"""
SurRender script
Script: demo_fullmoon.py
(C) 2021 Airbus copyright all rights reserved

SurRender Moon demo:
This script generates views of the Moon using a 118m resolution elevation map and an albedo map of the entire Moon.
The example displays a distant view from a camera positioned at a given longitude, latitude and altitude relative to the Moon centered on [0,0,0]. The same dataset can be used to simulate for example a descent trajectory, using setObjectPosition('camera', ...).
The first lines of the header describe how to generate the input from NASA PDS data (36 GB dataset).
"""

## GENERATING SURRENDER INPUT FROM NASA PDS DATA
# INPUT: 
# 1) FullMoon.img is the LRO/LOLA DEM dataset available at 118m for the entire Moon -->
#   https://astrogeology.usgs.gov/search/details/Moon/LRO/LOLA/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014/cub
#   see NASA PDS and Barker et al. 2016 (Icarus vol. 273)
#
#   The gen_input_fromIMG.sh script will generate height maps and conemaps in surrender .big format in double precision
#   For computing and memory efficiency, an additional step is taken to convert data in SurRender cf and half-float formats respectively.
#
# gen_input_fromIMG.sh:
#   Generate conemaps and elevation maps in .big 
#   build_conemap  FullMoon.img FullMoon.dem			# will create FullMoon.dem, FullMoon_heightmap.big and FullMoon_conemap.big

# Convert textures to half-precision (optional)
#  ./big_texture_converter_to_CF   FullMoon_heightmap.big FullMoon_heightmap_cf.big
#  ./big_texture_converter_to_half FullMoon_conemap.big FullMoon_conemap_half.big

# 2) Kaguya_MI_refl_b2_750nm_global_128ppd.big is an albedo map converted from -->   https://astrogeology.usgs.gov/search/map/Moon/Kaguya/MI/SpectralBands/Kaguya_MI_refl_b2_750nm_global_128ppd
# big_texture_builder Kaguya_MI_refl_b2_750nm_global_128ppd.tif Kaguya_MI_refl_b2_750nm_global_128ppd.big



## Starting SurRender script:
import numpy as np
from numpy import sin, cos, pi
import matplotlib.pyplot as plt
from surrender.surrender_client import surrender_client
from surrender.geometry import vec3, normalize, gaussian, quat, look_at
import time

ua = 149597870000
Moon_radius = 1737400.0;

s = surrender_client()
s.connectToServer('127.0.0.1', 5151) # A SurRender server must be on
s.closeViewer()

s.setConventions(s.XYZ_SCALAR_CONVENTION, s.Z_FRONTWARD)
s.setImageSize(1024,1024)
s.setCameraFOVDeg(70,70)
s.setCubeMapSize(512)
s.setShadowMapSize(1024)

s.createBRDF('sun', 'sun.brdf', {})
s.createShape("sun_shape", "sphere.shp", {'radius' : 1392000000.0 * 0.5})
s.createBody("sun", "sun_shape", "sun", {})
s.setObjectPosition("sun", normalize(vec3(1, 1, 0.1)) * ua)

s.createBRDF('raw', 'raw.brdf', {})
s.createBRDF('mate', 'mate.brdf', {})
s.createBRDF('hapke', 'hapke.brdf', {})
info = s.createSphericalDEM('moon', 'FullMoon_demi.dem', 'hapke', 'Kaguya_MI_refl_b2_750nm_global_128ppd.big')

CENTER_LATITUDE = (info['MINIMUM_LATITUDE'] + info['MAXIMUM_LATITUDE']) / 2.0 * (pi / 180.0);
CENTER_LONGITUDE = (info['WESTERNMOST_LONGITUDE'] + info['EASTERNMOST_LONGITUDE']) / 2.0 * (pi / 180.0);

DEM_ref_pos = vec3(cos(CENTER_LONGITUDE) * cos(CENTER_LATITUDE),
                   sin(CENTER_LONGITUDE) * cos(CENTER_LATITUDE),
                   sin(CENTER_LATITUDE)) * info['A_AXIS_RADIUS'];

p = pi * ua * ua * 6;
s.setSunPower([p,p,p,p])

s.enableRaytracing(True)
s.enablePathTracing(False)

s.loadPSFModel('gaussian.psf', {'sigma':0.6})
s.enableRegularPSFSampling(True)
s.setNbSamplesPerPixel(3)
s.enableRaySharing(True)

s.setFSAA(5)
s.setPSFSigma(0.6)

s.enablePreviewMode(True)

for k in info:
    print(k, " = ", info[k])

s.setObjectAttitude("camera", quat(vec3(1,0,0), pi/2)); # Init

moon_pos = vec3(0,0,0)
s.setObjectPosition('moon', moon_pos)
s.setObjectAttitude('moon', quat(vec3(1,0,0), 0))

frameID = 1;

start = time.clock_gettime(time.CLOCK_MONOTONIC)
frameCount = 0;

h = None

while True:
    t = frameID / 10.0;
    
    theta = t * pi * 0.2
    sun_pos = normalize(vec3(cos(theta),sin(theta),1)) * ua;
    s.setObjectPosition("sun", sun_pos)
    
		# Defines the camera position and viewing direction. look_at calculate the camera attitude.
    lat = 0 # camera lattitude
    lon = 0 # Camera longitude
		eye_pos = vec3(cos(lon) * cos(lat), sin(lon) * cos(lat), sin(lat)) * (Moon_radius + 2e6) # Camera altitude is Moon radius + 2e6m
    look_at(s, eye_pos, moon_pos)  # Put camera position to eye_pos, and auto-setup camera attitude to point at moon_pos
    
		# Render image:
    s.render()
		
		# Make plots:
    if h == None:
        h = plt.imshow(s.getImageGray32F(), cmap='gray', interpolation='none')
    else:
        h.set_data(s.getImageGray32F())
    plt.pause(0.01)
    
    if frameCount > 10:
        t = time.clock_gettime(time.CLOCK_MONOTONIC)
        fps = frameCount / (t - start)
        frameCount = 0;
        start = t;
    print(fps, " fps")
    print(frameID)
    frameID = frameID + 1
    frameCount = frameCount + 1
