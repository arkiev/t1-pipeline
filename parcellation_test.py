import os
import typing as ty
import pydra  
from pydra import Workflow, mark, ShellCommandTask
from pydra.engine.specs import File, Directory
from pydra.tasks.mrtrix3.v3_0 import labelconvert, labelsgmfix
from fileformats.medimage import NiftiGz, MghGz
# from fileformats.medimage_mrtrix3 import ImageFormat

import shutil
from pathlib import Path
import shutil
from fileformats.generic import Directory

# Define some filepaths
freesurfer_home="/Applications/freesurfer/"
mrtrix_lut_dir="/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert/"
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/v2_tests/'

# Define the input values using input_spec
input_spec = {"FS_dir": str, "parcellation": str} 

# Create a Pydra Workflow
wf = Workflow(name='my_workflow', input_spec=input_spec,cache_dir=output_path) 

###################################################################
# Annotate the task of getting the user defined parcellation type #
###################################################################

@mark.task
@mark.annotate({"parcellation": str, "return": {"fs_parc_image": str, "parc_lut_file": str, "mrtrix_lut_file": str, "output_parcellation_filename": str}})
def identify_parc(parcellation: str):
    # DESIKAN definitions
    if parcellation == 'desikan':
        fs_parc_image="aparc+aseg.mgz"
        parc_lut_file = os.path.join(freesurfer_home,'FreeSurferColorLUT.txt')
        mrtrix_lut_file = os.path.join(mrtrix_lut_dir,'fs_default.txt')
    # DESTRIEUX definitions
    elif parcellation == 'destrieux':
        fs_parc_image="aparc.a2009s+aseg.mgz"
        parc_lut_file = os.path.join(freesurfer_home,'FreeSurferColorLUT.txt')
        mrtrix_lut_file = os.path.join(mrtrix_lut_dir,'fs_a2009s.txt')
    #HCPMMP1 definitions
    elif parcellation =='hcpmmp1':
        fs_parc_image='' # NA for this parcellation scheme    
        parc_lut_file = os.path.join(mrtrix_lut_dir,'hcpmmp1_original.txt')
        mrtrix_lut_file = os.path.join(mrtrix_lut_dir,'hcpmmp1_ordered.txt')
    
    output_parcellation_filename=('parc_' + parcellation + '.mif' )
    print("parcellation type: ", parcellation)
    print("FS parcellation image: ", fs_parc_image)
    print("parc_lut_file: ", parc_lut_file)
    print("mrtrix_lut_file type: ", mrtrix_lut_file)
    print("output parcellation filename: ", output_parcellation_filename)

    return fs_parc_image, parc_lut_file, mrtrix_lut_file, output_parcellation_filename
    
# Add the task to the workflow
wf.add(identify_parc(parcellation=wf.lzin.parcellation, name="identifyparc_task"))
# wf.set_output(("output_identify_parc", wf.identifyparc_task.lzout.parc_image))

###############################################################################################
# Annotate the task of getting the relevant FS images (task of concatenating image filepaths) #
###############################################################################################

@mark.task
@mark.annotate({"fs_dir": str, "parc_image": str, "return": {"parcimg_path": str, "normimg_path": str}})
def join_paths(fs_dir: str, parc_image: str) -> str:
    parcimg_path=os.path.join(fs_dir, 'mri', parc_image)
    normimg_path=os.path.join(fs_dir, 'mri', "norm.mgz")
    print("Parcellation image filepath: ", parcimg_path)
    print("Norm image filepath: ", normimg_path)
    return parcimg_path, normimg_path
# Add the task to the workflow
wf.add(join_paths(fs_dir=wf.lzin.FS_dir, parc_image=wf.identifyparc_task.lzout.parc_image, name="join_task")) #FIX CASE of FS_dir!!

######################
# PARCELLATION EDITS #
######################

# relabel segmenetation to integers 
wf.add(
    labelconvert(
        path_in=wf.join_task.lzout.parcimg_path,
        lut_in=wf.identifyparc_task.lzout.parc_lut_file,
        lut_out=wf.identifyparc_task.lzout.mrtrix_lut_file,
        path_out="nodes.mif",
        name="LabelConvert_task"
    )
)

# # # # Replace FreeSurfer’s estimates of sub-cortical grey matter structures with estimates from FSL’s FIRST tool
wf.add(
    labelsgmfix(
        parc=wf.LabelConvert_task.lzout.path_out, 
        t1=wf.join_task.lzout.normimg_path,
        lut=wf.identifyparc_task.lzout.mrtrix_lut_file,
        output=wf.identifyparc_task.lzout.output_parcellation_filename,
        name="SGMfix_task",
        nocleanup=True,
        premasked=True,
        sgm_amyg_hipp=True
    )
)

########################
# Execute the workflow #
########################
# Set the workflow output as the result of the join_task
wf.set_output(("parcellation_image", wf.SGMfix_task.lzout.output))
# # wf.set_output(("parcellation_image", wf.LabelConvert_task.lzout.path_out))
# wf.set_output(("parcellation_image", wf.join_task.lzout.parcimg_path))

result = wf(
    FS_dir="/Users/arkievdsouza/git/t1-pipeline/working-dir/fastsurfer_3af71ff49c76c541ad541bf24fd2849d/subjects_dir/FS_outputs/",
    parcellation="desikan",
    plugin="serial",
)

print("Result:", result)
