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
import matplotlib.pyplot as plot
try:
    from surrender_test.util import config, with_pytest, s, script_dir
except Exception as e:
    print(e)

def test_render(with_pytest: bool, config, s, script_dir):
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
    use_sensor =  True
    rays = 128 # Rays per pixel (use rays > 128 for more realism)

    # set PSF
    surech_PSF=10
    sigma = 1
    wPSF = 5
    PSF = gaussian(wPSF * surech_PSF, sigma * surech_PSF)

    ## Initializing SurRender
    if not with_pytest:
        s = surrender_client()
    s.setVerbosityLevel(1)
    s.connectToServer('127.0.0.1')
    s.setCompressionLevel(0);
    s.closeViewer()
    s.setTimeOut(86400)

    s.setShadowMapSize(512)
    s.setCubeMapSize(512)
    s.enablePreviewMode(True)
    s.enableDoublePrecisionMode(False)
    s.enableRaytracing(True)

    if use_sensor == True:
      s.runLuaScript('sensors/GenericSensor.lua') # Loads sensor objects with configuration defined in the lua file
      s.runLuaCode('GenericSensor.config.ADC_gain = 2e-12') # Modifies ADC gain
      s.runLuaCode('GenericSensor:setup()') # Runs the setup function of GenericSensor.lua'

    s.setConventions(s.SCALAR_XYZ_CONVENTION,s.Z_FRONTWARD);
    s.setPSF(PSF,wPSF,wPSF)

    if raytracing:
        s.enableRaytracing(True)
        s.enableIrradianceMode(False)
        s.setNbSamplesPerPixel(rays) # Raytracing
        s.enableRegularPSFSampling(True)
        s.enablePathTracing(False)
    else:
        s.enableRaytracing(False)
        s.enableIrradianceMode(False)
        s.enablePathTracing(False)

    s.createBRDF('sun', 'sun.brdf', {})
    s.createShape('sun', 'sphere.shp', { 'radius' : sun_radius })
    s.createBody('sun', 'sun', 'sun', [])
    s.setSunPower(8*ua*ua*pi*5.2*5.2*vec4(1,1,1,1))

    s.createBRDF('hapke', 'hapke.brdf', {})
    s.createMesh('asteroid', 'itokawa_small.obj', 1e3)
    s.setObjectElementBRDF('asteroid', 'asteroid', 'hapke')

    s.setCameraFOVDeg(fov, np.arctan(np.tan(fov/360*pi)*N[1]/N[0])*360/pi)
    s.setImageSize(N[0],N[1])

    Rcam = np.eye(3)
    s.setObjectPosition('camera', vec3(0,0,0))
    s.setObjectAttitude('camera', MatToQuat(Rcam))
    s.setObjectPosition('sun', pos_sun)
    s.setObjectPosition('asteroid', pos_target)

    # Defines the attitude of the asteroid (quaternion):
    R_ast = np.eye(3)
    R_ast = QuatToMat(quat(vec3(1,0,0), pi/2)) @ R_ast
    R_ast = QuatToMat(quat(vec3(0,1,0), -pi/2)) @ R_ast
    R_ast = QuatToMat(quat(vec3(0,1,0), -pi/8)) @ R_ast
    R_ast = QuatToMat(quat(vec3(0,0,1), pi/4)) @ R_ast
    R_ast = QuatToMat(quat(vec3(1,0,0), -pi/3)) @ R_ast
    R_ast = QuatToMat(quat(vec3(0,1,0), -pi/5)) @ R_ast
    s.setObjectAttitude('asteroid', MatToQuat(R_ast))

    if use_sensor:
      print('Rendering image with sensor model:')
      # use sensor with SurRender 6.1 because of gain definition compatibility
      s.runLuaCode('GenericSensor:render()') # Runs the render function of GenericSensor.lua'
    else:
      print('Rendering sensorless image:')
      s.render()

    im = s.getImageSpectrumProjection( [1,0,0,0] )

    if with_pytest:
        from surrender_test.check import check_img_error_hist
        check_img_error_hist(config, im, f"{script_dir}/../../surrender-nonreg-test/user_manual/control/SCR08_ref_wsensor.tif")
    else:
        cv2.imwrite('SCR08_itokawa_wsensor.png', np.array(np.clip(im * (255 / np.max(im)), 0, 255), dtype=np.uint8))

        print(np.min(im))
        print(np.max(im))
        print(np.median(im))
        # Display and save image:
        plot.ioff()
        plot.imshow(im, aspect='equal', interpolation='none', cmap='gray');
        plot.draw()

if __name__ == "__main__":
    test_render(False, None, None, None)
