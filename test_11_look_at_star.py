#! python3
# -*- coding: utf-8 -*-
"""
 SurRender
 Script: SCR_11 Look at star
 (C) 2021 Airbus copyright all rights reserved

 This script simulates an image of the sky around a given star defined by its (right ascension, declination) coordinates. Some coordinates are provided as example.
 
 It uses a star chart where each row describes a star with the 7 following values:
 - columns 0-2: the x, y, z LoS coordinates expressed in the J2000 frame;
 - columns 3-6: spectral irradiance split on 4 wavebands (for instance, these components can be [total_irradiance, 0, 0, 0] for panchromatic rendering).
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys

from surrender.surrender_client import surrender_client
from surrender.geometry import vec3, vec4, quat, quaternion_from_vec_to_vec, gaussian, normalize, look_at_star
try:
    from surrender_test.util import config, with_pytest, s, script_dir
except Exception as e:
    print(e)

# ----------------------------------------------------------------------------------------------------------------------

EXAMPLE_STAR_COORDINATES = { 
    # star: (RA, dec)
    'CanisMajor_Sirius': ('6_45_8.91728', '-16_42_58.02'),
    'Crux_beta': ('12_47_43.32', '-59_41_19.4'),
    'Lyra_Vega' : ('18_36_56.33635', '38_47_01.2802'),
    'Orion_Alnilam': ('5_36_12.81', '-1_12_6.9'),
    'Orion_Betelgeuse': ('5_55_10.29', '7_24_25.3'),
    'UrsaMajor_alpha': ('12_54_1.63', '55_57_35.4'),
}

# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------
def test_render(with_pytest: bool, config, s, script_dir):

    do_plot = True
    do_save = False

    # --[Connection to server]---------------------------------------------------------
    if not with_pytest:
        s = surrender_client()
    s.setVerbosityLevel(1)
    s.connectToServer('127.0.0.1', 5151)

    print('--------------------------------------')
    print('SCRIPT : %s'%sys.argv[0])
    print('SurRender version: ' + s.version())
    print('--------------------------------------')

    # --[PSF definition]---------------------------------------------------------------
    PSFsize = 11
    sigma = 0.25
    psf = np.array(range(PSFsize)) - int(PSFsize / 2)
    psf = np.meshgrid(psf, psf)
    psf = np.exp(-(psf[0] ** 2 + psf[1] ** 2) / (2. * sigma ** 2))
    psf = psf / np.sum(psf)
    row, col = psf.shape
    dist = int(max(row, col) / 2) + 2

    # --[Initialization]---------------------------------------------------------------
    s.reset()
    s.closeViewer()
    s.setConventions(s.SCALAR_XYZ_CONVENTION, s.Z_FRONTWARD)
    s.setCompressionLevel(0)
    s.enableRaytracing(True)
    s.enablePreviewMode(False)
    s.enableIrradianceMode(True)
    s.setNbSamplesPerPixel(128)
    s.setTimeOut(3600)

    # --[Camera]-----------------------------------------------------------------------
    pos_cam = np.array([0, 0, 0])
    s.setObjectPosition('camera', pos_cam)

    # --[FoV configuration]------------------------------------------------------------
    xFOV = 45 # deg
    yFOV = 45 # deg
    s.setCameraFOVDeg(xFOV, yFOV)

    # --[Image size]-------------------------------------------------------------------
    IMAGE_SIZE = 1024
    s.setImageSize(IMAGE_SIZE, IMAGE_SIZE)

    # --[PSF creation]-----------------------------------------------------------------
    s.setPSF(psf, row, col, dist)
    s.enableRegularPixelSampling(True)

    # --[Star map]---------------------------------------------------------------------
    starmap = 'tycho-2_V_corrected.bin' # Update star map filename
    s.setBackground(starmap)

    # --[Point camera towards star]----------------------------------------------------
    target_star = 'Orion_Alnilam' # Select star name from EXAMPLE_STAR_COORDINATES
    ra, dec = EXAMPLE_STAR_COORDINATES[target_star]
    look_at_star(s, ra, dec)

    # --[Rendering]--------------------------------------------------------------------
    s.render()

    # --[Image recovery]---------------------------------------------------------------
    image = s.getImageGray32F()

    if with_pytest:
        from surrender_test.check import check_img_error_hist
        check_img_error_hist(config, image, f"{script_dir}/../../surrender-nonreg-test/user_manual/control/SCR11_ref.tif")
    else:
        if do_plot:
            plt.imshow(image, cmap='gray', interpolation='none', vmax=image.max() / 10)
            plt.show()
        if do_save:
            Image.fromarray(image).save(f'look_at_{target_star}.tif')

    print('SCR_11: done.')
    print('--------------------------------------')

if __name__ == "__main__":
    test_render(False, None, None, None)
# ----------------------------------------------------------------------------------------------------------------------
# End
