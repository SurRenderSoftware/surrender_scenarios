#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 SurRender script
 Script :
 (C) 2023 Airbus copyright all rights reserved
 # Test to estimate the calculation time of a rendering in raytracing in normal condition 
 # versus ith optimized conditions (StdDevThreshold SurRender function) in an example scene
"""

import os
import math
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from surrender.surrender_client import surrender_client
from surrender.geometry import normalize, vec3, vec4, quat
import time
try:
    from surrender_test.util import config, with_pytest, s, script_dir
except Exception as e:
    print(e)

# Image Normalization
def normalize_map8bit(map):
    mx = np.max(map[np.isfinite(map)])
    mn = np.min(map[np.isfinite(map)])
    mapNorm = ((map - mn) / (mx - mn) * 255).astype(np.uint8)
    return mapNorm

def test_render(with_pytest: bool, config, s, script_dir):
    activate_stdthresh = True

    n_rays = 1000
    fov = 20 # degrees
    fov_x, fov_y = fov, fov
    npix = [1024, 1024]

    # INITIALIZE SURRENDER
    print("Initialize SurRender")
    if not with_pytest:
        s = surrender_client()
    s.setVerbosityLevel(3)
    s.connectToServer('127.0.0.1', 5151)
    s.record()
    s.setCompressionLevel(0)
    s.closeViewer()
    s.setTimeOut(3600 * 2)
    s.enablePhotonAccumulation(False)
    s.setSelfVisibilitySamplingStep(5)
    s.setPhotonMapSamplingStep(5)
    s.enableLOSmapping(True)
    s.enableRaytracing(True)
    s.enablePathTracing(False)
    s.enablePreviewMode(False)
    s.enableVarianceMapping(True)
    s.setNbSamplesPerPixel(n_rays)
    s.setShadowMapSize(512)
    s.setCubeMapSize(512)
    s.setCameraFOVDeg(fov_x, fov_y)
    s.setImageSize(npix[0], npix[1])
    s.enableIrradianceMode(False)
    s.setIntegrationTime(0.2)


    # BRDF
    s.createBRDF("mate", "mate.brdf", {})
    s.createBRDF('oren_nayar_itokawa', 'oren_nayar.brdf', {'albedo': 0.3})
    s.setConventions(s.SCALAR_XYZ_CONVENTION, s.Z_FRONTWARD)

    # Sun
    UA = 149597870000
    s.createBRDF('sun', 'sun.brdf', {})
    power = 0.5*UA*UA*1367
    s.createShape("sun_shape", "sphere.shp", {'radius': 6.96342e8})
    s.createBody("sun", "sun_shape", "sun", {})
    s.setSunPower([power] * 4)
    pos_sun = normalize(vec3(1, -1, -2)) * 8e11
    s.setObjectPosition("sun", pos_sun)

    # Target
    s.createMesh('itokawa', 'itokawa_small.obj', 1000)
    s.setObjectElementBRDF('itokawa', 'itokawa', 'oren_nayar_itokawa')
    pos_obj, quat_obj = np.array([0., 0., 1000.]), np.array([1., 0., 0., 0.])
    s.setObjectPosition("itokawa", pos_obj)
    s.setObjectAttitude("itokawa", quat_obj)

    # Sensor
    pos_cam = vec3(0., 0., 0.)
    s.setObjectPosition('camera', pos_cam)
    s.setObjectAttitude('camera', quat(vec3(1., 0., 0.), 0.))


    # Simulation 1 : NO THRESHOLD
    clock = time.time()
    s.render()
    im = s.getImage()
    clock2 = time.time()
    print("Nrays", n_rays)
    im1 = normalize_map8bit(im)
    v_map1 = s.getVarianceMap()
    print("Time of execution:", clock2 - clock, "s")


    # Simulation 2 : STD THRESHOLD
    s.setStdDevThreshold(1e-4)
    s.render()
    im = s.getImage()
    clock3 = time.time()
    print("Nrays", n_rays)
    print("Time of execution:", clock3 - clock2, "s")
    im2 = normalize_map8bit(im)
    v_map2 = s.getVarianceMap()
    print("Max variance map value no std threshold", np.max(np.mean(v_map1, axis=2)))
    print("Max variance map value with std threshold", np.max(np.mean(v_map2, axis=2)))

    if with_pytest:
        from surrender_test.check import check_img_error_hist
        check_img_error_hist(config, im1[...,:3], f"{script_dir}/../../surrender-nonreg-test/user_manual/control/SCR13_1_ref.png")
        check_img_error_hist(config, im2[...,:3], f"{script_dir}/../../surrender-nonreg-test/user_manual/control/SCR13_2_ref.png")
    else:
        plt.figure(1)
        plt.imshow(im1[:, :, 0:3])
        plt.figure(2)
        plt.imshow(np.mean(v_map1, axis=2))
        plt.figure(3)
        plt.imshow(im2[:, :, 0:3])
        plt.figure(4)
        plt.imshow(np.mean(v_map2, axis=2))
        plt.show()

        diff_vmap = np.absolute(np.mean(v_map1, axis=2) - np.mean(v_map2, axis=2))

        Image.fromarray(im1[:, :, 0:3]).save("SCR13_image_nostd_threshold.png")
        Image.fromarray(im2[:, :, 0:3]).save("SCR13_image_std_threshold.png")

if __name__ == "__main__":
    test_render(False, None, None, None)
