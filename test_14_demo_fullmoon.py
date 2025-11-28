#! python3
# -*- coding: utf-8 -*-
"""
SurRender script
Script: demo_fullmoon.py
(C) 2021 Airbus copyright all rights reserved

SurRender Moon demo:
This script generates views of the Moon using a 118m resolution elevation map and an albedo map of the entire Moon.
The example displays a distant view from a camera positioned at a given longitude, latitude and altitude relative to the Moon centered on [0,0,0]. The same dataset can be used to simulate for example a descent trajectory, using setObjectPosition('camera', ...).
The first lines of the header describe how to generate the input from NASA PDS data.

### GENERATING SURRENDER INPUT FROM NASA PDS DATA

FullMoon.img is the LRO/LOLA DEM dataset available at 118m for the entire Moon -->
https://astrogeology.usgs.gov/search/map/moon_lro_lola_dem_118m
see NASA PDS and Barker et al. 2016 (Icarus vol. 273)

In order to generate heightmap & conemap in double precision, use the following commands:

    # will create FullMoon.dem, FullMoon_heightmap.big, FullMoon_conemap.big
    build_conemap_spherical FullMoon.img FullMoon.dem

    # move them to surrender resource path
    mkdir <surrender path>/DEM
    mv FullMoon.dem <surrender path>/DEM/
    mv FullMoon_heightmap.big <surrender path>/textures/
    mv FullMoon_conemap.big <surrender path>/textures/

    # create texture for reflectance map in BIG format
    big_texture_builder Kaguya_MI_refl_b2_750nm_global_128ppd.tif <surrender path>/textures/Kaguya_MI_refl_b2_750nm_global_128ppd.big

"""

## Starting SurRender script:
import numpy as np
from numpy import sin, cos, pi
import matplotlib.pyplot as plt
from surrender.surrender_client import surrender_client
from surrender.geometry import vec3, normalize, gaussian, quat, look_at
import time

ua = 149597870000
Moon_radius = 1737400.0;

def main():
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

    s.createBRDF('hapke', 'hapke.brdf', {})
    info = s.createSphericalDEM('moon', 'FullMoon.dem', 'hapke', 'Kaguya_MI_refl_b2_750nm_global_128ppd.big')

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

    moon_pos = vec3(0,0,0)
    s.setObjectPosition('moon', moon_pos)
    s.setObjectAttitude('moon', quat(vec3(1,0,0), 0))

    frameID = 1;

    start = time.clock_gettime(time.CLOCK_MONOTONIC)
    frameCount = 0;

    h = None
    fps=0

    while True:
        t = frameID / 10.0;

        theta = t * pi * 0.2
        sun_pos = normalize(vec3(cos(theta),sin(theta),1)) * ua;
        s.setObjectPosition("sun", sun_pos)

        # Defines the camera position and viewing direction. look_at calculate the camera attitude.
        lat = 0 # camera lattitude
        lon = 0 # Camera longitude
        eye_pos = vec3(cos(lon) * cos(lat), sin(lon) * cos(lat), sin(lat)) * (Moon_radius + 2e6) # Camera altitude is Moon radius + 2e6m
        look_at(s, eye_pos, moon_pos, up=(0,0,1))  # Put camera position to eye_pos, and auto-setup camera attitude to point at moon_pos

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

if __name__ == "__main__":
    main()
