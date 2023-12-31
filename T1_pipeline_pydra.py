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
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/v1_tests/'

# Define the input_spec for the workflow
input_spec = {"t1w": NiftiGz, "fs_license": File, "sub_ID": str, "default_file": File, "freesurfer_LUT": File, "segmentation": MghGz} 
output_spec = {"fTT_image": ImageFormat,"vis_image": ImageFormat,  "parc_image": ImageFormat}

# Create a workflow 
wf = Workflow(name='T1preproc_workflow', input_spec=input_spec, cache_dir=output_path, output_spec=output_spec) 

# FastSurfer Task
wf.add(
    fastsurfer(
        T1_files=wf.lzin.t1w, 
        fs_license=wf.lzin.fs_license,
        subject_id="FS_outputs",
        name="FastSurfer_task",
        py="python3.11",
        norm_img="norm.mgz",
        aparcaseg_img="aparcaseg.mgz",
        fsaparc=True,
        parallel=True,
        threads=24,
    )    
)

# #################################################
# # Five Tissue Type Generation and visualisation #
# #################################################

# Five tissue-type task
wf.add(
    fivettgen_hsvs(
        input=wf.FastSurfer_task.lzout.subjects_dir_output, 
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

# ###################
# # DK parcellation #
# ###################

# relabel segmenetation to integers indexed from 1 to 84
wf.add(
    labelconvert(
        path_in=wf.FastSurfer_task.lzout.aparcaseg_img,
        lut_in=wf.lzin.freesurfer_LUT,
        lut_out=wf.lzin.default_file,
        path_out="nodes.mif",
        name="LabelConvert_task"
    )
)

# # Replace FreeSurfer’s estimates of sub-cortical grey matter structures with estimates from FSL’s FIRST tool
wf.add(
    labelsgmfix(
        parc=wf.LabelConvert_task.lzout.path_out, 
        t1=wf.FastSurfer_task.lzout.norm_img,
        lut=wf.lzin.default_file,
        output="parcellation_image_DK_unregistered.mif",
        name="SGMfix_task",
        nocleanup=True,
        premasked=True,
        sgm_amyg_hipp=True
    )
)

###################
## WORKFLOW SETUP #
###################

wf.set_output(("fTT_image", wf.fTTgen_task.lzout.output.cast(ImageFormat)))
wf.set_output(("vis_image", wf.fTTvis_task.lzout.output.cast(ImageFormat)))
wf.set_output(("parc_image", wf.SGMfix_task.lzout.output.cast(ImageFormat)))

# ## Execute the workflow (FastSurfer, NIF data)
# result = wf(
#     t1w="/Users/arkievdsouza/Documents/NIFdata/ds000114/sub-01/ses-retest/anat/sub-01_ses-retest_T1w.nii.gz",
#     fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
#     sub_ID="sub-01_ses-retest",
#     default_file="/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert/fs_default.txt",
#     freesurfer_LUT="/Applications/freesurfer/FreeSurferColorLUT.txt",
#     plugin="serial"
# )

# # Execute the workflow (FastSurfer, HCP data)
# result = wf(
#     t1w="/Users/arkievdsouza/Documents/100307/100307_FastSurfer/mri/orig.nii.gz",
#     fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
#     sub_ID="100307",
#     default_file="/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert/fs_default.txt",
#     freesurfer_LUT="/Applications/freesurfer/FreeSurferColorLUT.txt",
#     # segmentation="/Users/arkievdsouza/git/t1-pipeline/working-dir/fastsurfer_0425d50a2d1bdc642ef8feb235ec3855/subjects_dir/100307/mri/aparc.DKTatlas+aseg.deep.mgz",
#     plugin="serial",
# )

# Execute the workflow (FastSurfer, Siemans data)
result = wf(
    t1w="/Users/arkievdsouza/Desktop/FastSurferTesting/data/sub-01_T1w_pos.nii.gz",
    fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
    sub_ID="sub-01",
    default_file="/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert/fs_default.txt",
    freesurfer_LUT="/Applications/freesurfer/FreeSurferColorLUT.txt",
    # segmentation="/Users/arkievdsouza/git/t1-pipeline/working-dir/fastsurfer_0425d50a2d1bdc642ef8feb235ec3855/subjects_dir/100307/mri/aparc.DKTatlas+aseg.deep.mgz",
    plugin="serial",
)


## RUN THIS script, check it works
# create a copy, call copy _parc_append or something
# add in catalogue of parcellation files