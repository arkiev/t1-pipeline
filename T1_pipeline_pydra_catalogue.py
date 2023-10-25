import os
import typing as ty
import pydra  
from pydra import Workflow, mark  
from pydra.engine.specs import File, Directory
from pydra.tasks.mrtrix3.v3_0 import fivett2vis, fivettgen_hsvs, labelconvert, labelsgmfix, mrconvert
from fileformats.medimage import NiftiGz, MghGz
from fileformats.medimage_mrtrix3 import ImageFormat
from pydra.tasks.fastsurfer.latest import fastsurfer
import shutil
from pathlib import Path
import shutil
from fileformats.generic import Directory
from fileformats.medimage import MghGz
from pydra import mark

# Define the path and output_path variables
# path = '/Users/arkievdsouza/Documents/NIFdata/ds000114'
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir'
mrtrix_lut_dir = '/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert'
freesurfer_home = '/Applications/freesurfer'
# Define the input_spec for the workflow
input_spec = {"t1w": NiftiGz, "fs_license": File, "sub_ID": str, "shared_parcellation": str, "FS_dir": str} 
output_spec = {"fTT_image": ImageFormat,"vis_image": ImageFormat,  "parc_image": ImageFormat}

# Create a workflow 
wf = Workflow(name='T1preproc_workflow', input_spec=input_spec, cache_dir=output_path, output_spec=output_spec) 

# # FastSurfer Task
# wf.add(
#     fastsurfer(
#         T1_files=wf.lzin.t1w, 
#         fs_license=wf.lzin.fs_license,
#         subject_id="FS_outputs",
#         name="FastSurfer_task",
#         py="python3.11",
#         norm_img="norm.mgz",
#         aparcaseg="aparcaseg.mgz",
#         # surf_only=True,
#         # seg=wf.lzin.segmentation,
#         # parallel=True,
#     )    
# )

# #################################################
# # Five Tissue Type Generation and visualisation #
# #################################################

# Five tissue-type task
wf.add(
    fivettgen_hsvs(
        input=wf.lzin.FS_dir, 
        output="fTT_hsvs.mif",
        name="fTTgen_task",
        nocrop=True,
        nocleanup=True,
        white_stem=True
    )
)

# Five tissue-type visualisation task
wf.add(
    fivett2vis(
        input=wf.fTTgen_task.lzout.output.cast(ImageFormat),
        output="fTT_hsvs_vis.mif",
        name="fTTvis_task"
    )
)




###################
## WORKFLOW SETUP #
###################

wf.set_output(("fTT_image", wf.fTTgen_task.lzout.output.cast(ImageFormat)))
wf.set_output(("vis_image", wf.fTTvis_task.lzout.output.cast(ImageFormat)))
wf.set_output(("parc_path_str", wf.join_task.lzout.out))
# wf.set_output(("parc_image", wf.SGMfix_task.lzout.output.cast(ImageFormat)))

# ## Execute the workflow (FastSurfer, NIF data)
# result = wf(
#     t1w="/Users/arkievdsouza/Documents/NIFdata/ds000114/sub-01/ses-retest/anat/sub-01_ses-retest_T1w.nii.gz",
#     fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
#     sub_ID="sub-01_ses-retest",
#     plugin="serial"
# )

# # Execute the workflow (FastSurfer, HCP data)
# result = wf(
#     t1w="/Users/arkievdsouza/Documents/100307/100307_FastSurfer/mri/orig.nii.gz",
#     fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
#     sub_ID="100307",
#     default_file="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/fs_default.txt",
#     freesurfer_LUT="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FreeSurferColorLUT.txt",
#     # segmentation="/Users/arkievdsouza/git/t1-pipeline/working-dir/fastsurfer_0425d50a2d1bdc642ef8feb235ec3855/subjects_dir/100307/mri/aparc.DKTatlas+aseg.deep.mgz",
#     plugin="serial",
# )

# Execute the workflow (FastSurfer, siemans data)
result = wf(
    t1w="/Users/arkievdsouza/Desktop/FastSurferTesting/data/sub-01_T1w_pos.nii.gz",
    fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
    sub_ID="sub-01",
    shared_parcellation="desikan", 
    plugin="serial",
    FS_dir="/Users/arkievdsouza/git/t1-pipeline/working-dir/fastsurfer_3af71ff49c76c541ad541bf24fd2849d/subjects_dir/FS_outputs/",
)

print("Result:", result)

