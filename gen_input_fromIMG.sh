## GENERATING SURRENDER INPUT FROM NASA PDS DATA
# INPUT: FullMoon.img is the LRO/LOLA DEM dataset available at 118m for the entire Moon
# (see NASA PDS and Barker et al. 2016 (Icarus vol. 273)
#
# The script will generate heightmaps and conemaps in surrender .big format in double precision
# For computing and memory efficiency, an additional step is taken to convert this data in SurRender cf and half-float format respectively

# Generate conemaps and elevation maps in .big 
# will create files FullMoon.dem, FullMoon_heightmap.big and FullMoon_conemap.big
./bin/build_conemap_spherical  ./DATA/FullMoon.img ./DEM/FullMoon.dem

# Convert textures in half-precision (optional)
./bin/big_texture_converter_to_CF   ./DATA/FullMoon_heightmap.big ./textures/FullMoon_heightmap_cf.big
./bin/big_texture_converter_to_half ./DATA/FullMoon_conemap.big ./textures/FullMoon_conemap_half.big

# ! You must edit the file ./DEM/FullMoon.dem to control paths 
echo "! You must edit the file ./DEM/FullMoon.dem to control paths !"

# Convert albedo map
./bin/big_texture_builder ./DATA/Kaguya_MI_refl_b2_750nm_global_128ppd.tif ./textures/Kaguya_MI_refl_b2_750nm_global_128ppd.big
