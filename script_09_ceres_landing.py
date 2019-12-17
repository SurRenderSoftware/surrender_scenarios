#! python3
# -*- coding: utf-8 -*-
"""
 SurRender script
 Script : SCR_09 Landing on Ceres
 (C) 2019 Airbus copyright all rights reserved
"""
from surrender.surrender_client import surrender_client
from surrender.geometry import vec3, vec4, quat, normalize, QuatToMat, MatToQuat, gaussian
import numpy as np
import matplotlib.pyplot as plot
import cv2
from PIL import Image

# Constants:
sun_radius = 696342000
ua2km = 149597870.700
ua = ua2km * 1000
Rceres = 4.7e5
pi = np.pi
pos_sun = normalize(vec3(-4e11,-4e11,-8e11)) * 8e11
pos_target = vec3(0,0,0)

# Image setup:
fov=5;
raytracing=True;
N = [512,512];
rays = 16;

# set PSF
surech_PSF=10;
sigma = 1;
wPSF = 5;
PSF = gaussian(wPSF * surech_PSF, sigma * surech_PSF);

## Initializing SurRender
s = surrender_client();
s.setVerbosityLevel(2);
s.connectToServer('127.0.0.1');
s.setCompressionLevel(0);
s.closeViewer();
s.setTimeOut(86400);
s.setShadowMapSize(512);
s.setCubeMapSize(512);
s.enableMultilateralFiltering(False);
s.enablePreviewMode(True);
s.enableDoublePrecisionMode(False);
s.enableRaytracing(True);

s.setConventions(s.SCALAR_XYZ_CONVENTION,s.Z_FRONTWARD);
s.setPSF(PSF,wPSF,wPSF);

if raytracing:
    s.enableFastPSFMode(False);
    s.enableRaytracing(True);
    s.enableIrradianceMode(False);
    s.setNbSamplesPerPixel(rays); # Raytracing
    s.enableRegularPSFSampling(True);
    s.enablePathTracing(False);
else:
    s.enableFastPSFMode(True);
    s.enableRaytracing(False);
    s.enableIrradianceMode(False);
    s.enablePathTracing(False);

s.createBRDF('sun', 'sun.brdf', {})
s.createShape('sun', 'sphere.shp', { 'radius' : sun_radius })
s.createBody('sun', 'sun', 'sun', []);

s.createBRDF('hapke', 'hapke.brdf', {})
s.createSphericalDEM('asteroid', 'Ceres_Dawn.dem', 'hapke', 'Ceres_texture.big')
s.setObjectElementBRDF('asteroid', 'asteroid', 'hapke')

s.setCameraFOVDeg(fov, np.arctan(np.tan(fov/360*pi)*N[1]/N[0])*360/pi);
s.setImageSize(N[0],N[1]);

s.setSunPower(10*ua*ua*pi*5.2*5.2*vec4(1,1,1,1));

## Trajectory
def gen_image(alpha, dist):
    Rcam = np.eye(3);
    s.setObjectPosition('camera', vec3(0,0,-dist));
    s.setObjectAttitude('camera', MatToQuat(Rcam));
    s.setObjectPosition('sun', pos_sun);
    s.setObjectPosition('asteroid', pos_target);

    R_ast = np.eye(3);
    R_ast = QuatToMat(quat(vec3(0,0,1), pi/2)) @ R_ast;
    R_ast = QuatToMat(quat(vec3(1,0,0), (90-11)/180*pi)) @ R_ast;
    R_ast = QuatToMat(quat(vec3(0,1,0), -alpha-pi/3)) @ R_ast;
    s.setObjectAttitude('asteroid', MatToQuat(R_ast));
   
    s.render();	
    im = s.getImageGray32F();
    
    ## Color
    imageRGBA = s.getImageRGBA8()
    # discards the alpha channel:
    r,g,b,a = Image.fromarray(imageRGBA).split()
    imageRGB = Image.merge("RGB", (r, g, b))
    im = imageRGB;

    im.save('images/' + 'ceres' + '_' + str(it).zfill(4) +'.png')
    #    
    plot.ioff()
    plot.imshow(im, aspect='equal', interpolation='none', cmap='gray');
    plot.draw()
    plot.pause(0.01)   


for it in range(0,359,1):
    angle = it / 360 * pi; # 1 degr steps
    dist = Rceres*(40-it/360*39);
    gen_image(angle, dist)
    print(str(round(it/360*100))+'%: '+ ' #'+str(it)+' -> '+str(round(dist/1000))+' km')

print(' End of simulation')
