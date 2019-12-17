#! python3
# -*- coding: utf-8 -*-
"""
 SurRender script
 Script : SCR_08 Itokawa
 (C) 2019 Airbus copyright all rights reserved
"""
from surrender.surrender_client import surrender_client
from surrender.geometry import vec3, vec4, quat, normalize, QuatToMat, MatToQuat, gaussian
import numpy as np
import cv2

# Constants:
sun_radius = 696342000
ua2km = 149597870.700
ua = ua2km * 1000
pi = np.pi
pos_sun = normalize(vec3(4e11,-4e11,-8e11)) * 8e11
pos_target = vec3(0,0,1e4)

# Image setup:
fov=5
raytracing=True
N = [768, 1024]

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

s.createBRDF('sun', 'sun.brdf', {})
s.createShape('sun', 'sphere.shp', { 'radius' : sun_radius })
s.createBody('sun', 'sun', 'sun', [])
s.setSunPower(8*ua*ua*pi*5.2*5.2*vec4(1,1,1,1))

s.createBRDF('hapke', 'hapke.brdf', {})
s.createMesh('asteroid', 'itokawa_f3145728.obj', 1e3)
s.setObjectElementBRDF('asteroid', 'asteroid', 'hapke')

s.setCameraFOVDeg(fov, np.arctan(np.tan(fov/360*pi)*N[1]/N[0])*360/pi)
s.setImageSize(N[0],N[1])

def gen_image(alpha, beta):
    Rcam = np.eye(3)
    s.setObjectPosition('camera', vec3(0,0,0))
    s.setObjectAttitude('camera', MatToQuat(Rcam))
    s.setObjectPosition('sun', pos_sun)
    s.setObjectPosition('asteroid', pos_target)
    R_ast = np.eye(3)
    R_ast = QuatToMat(quat(vec3(1,0,0), pi/2)) @ R_ast
    R_ast = QuatToMat(quat(vec3(0,1,0), -pi/2)) @ R_ast
    R_ast = QuatToMat(quat(vec3(0,1,0), -pi/8)) @ R_ast
    R_ast = QuatToMat(quat(vec3(0,0,1), pi/4)) @ R_ast
    R_ast = QuatToMat(quat(vec3(1,0,0), -pi/3)) @ R_ast
    R_ast = QuatToMat(quat(vec3(0,1,0), -pi/5)) @ R_ast
    s.setObjectAttitude('asteroid', MatToQuat(R_ast))
    s.render()
    
gen_image(-pi/12, pi/6)
im = s.getImageGray32F()
cv2.imwrite('itokawa.png', np.array(np.clip(im * (255 / np.max(im)), 0, 255), dtype=np.uint8))
