# SurRender software examples

The SurRender software is a powerful image renderer developed by the Image Processing Advanced Studies team of Airbus Defence & Space.
It is specially designed for space applications such as vision-based navigation (planetary approach and landing, in orbit rendezvous, etc.). 
It uses raytracing (CPU) or openGL (GPU) and it is highly optimized for space simulations (sparse scenes, reflections and shadows, large distance dynamics, huge datasets). 
Users can input various data at standard formats (Digital Elevation Models, images, meshes), and configure models for various properties such as materials and sensors (shutter type, noises, integration time, etc.). SurRender simulations aim at physical representativeness as needed for the development and validation of  computer vision algorithms.
This GitHub project gathers examples of scenarios the can be simulated by the SurRender software with the Python API.

## Getting Started
The SurRender client API may be dowloaded from GitHub [surrender_client project](https://github.com/SurRenderSoftware/surrender_client_API).
A selection of tests is provided in this project. They are coded in Python. They range from installation and basic tests to advanced simulaions of 3D objects (meshes and DEMs):

script_00_installation_control.py  script_01_rendering_a_sphere.py      script_02_simple_earth_sun_camera_system.py
script_03_summer_solstice.py       script_04_raytracing_precision.py    script_05_psf.py
script_06_tycho_background.py      script_07_stellar_background.py      script_08_itokawa_mesh.py
script_09_ceres_landing.py

## Prerequisite
A standard Python3 installation is required, e.g. Anaconda.
The server is delivered with all the needed dependencies.

## Running the tests
Start the server in a terminal by running:
`./start_server.sh`
Run tests in Python by executing for exemple:
`python3 script_00_installation_control.py`

## Contributing
Users are invited to share their scenarios in a format similar to the available examples such as script_08_itokawa_mesh.py and script_09_ceres_landing.py
Self-sufficient explanation should be provided in order to retrieve the needed data.

## License
This project is licensed under the Apache License Version 2.0 of January 2004. See the LICENSE file for details.
(C) 2019 Airbus copyright all rights reserved

## References
Information about the software is available at https://www.airbus.com/SurRenderSoftware.html
https://arxiv.org/abs/1810.01423 

