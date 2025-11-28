SCRIPTS=${wildcard scr*.py SCR*.py}

EXEC=python3

.PHONY: all clean SCR00 SCR01 SCR02 SCR03 SCR04 SCR05 SCR06 SCR07 SCR08

all: SCR00 SCR01 SCR02 SCR03 SCR04 SCR05 SCR06 SCR07 SCR08


# this is compatible with make -j XX
SCR00: script_00_installation_control.py
	./$^

SCR01: script_01_rendering_a_sphere.py
	./$^

SCR02: script_02_simple_earth_sun_camera_system.py
	./$^

SCR03: script_03_summer_solstice.py
	./$^

SCR04: script_04_raytracing_precision.py
	./$^

SCR05: script_05_psf.py
	./$^

SCR06: script_06_tycho_background.py
	./$^

SCR07: script_07_stellar_background.py
	./$^


clean:
	rm -rf SCR*.txt SCR*.png SCR*.tif
