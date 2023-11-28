import os
import typing as ty
import pydra  
from pydra import Workflow, mark  
from pydra.engine.specs import File, Directory
from pydra.tasks.freesurfer.auto import ApplyMask
from fileformats.medimage import NiftiGzXBvec, NiftiGz


# Define the path and output_path variables
# path = '/Users/arkievdsouza/Documents/NIFdata/ds000114'
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/test_applymask'
input_spec = {"t1w": File, "mask": File} 
output_spec = {"out_file": File}

# Create a workflow 
wf = Workflow(name='mask_image', input_spec=input_spec, cache_dir=output_path, output_spec=output_spec) 

# # FastSurfer Task
wf.add(
    ApplyMask(
        in_file=wf.lzin.t1w,
        mask_file=wf.lzin.mask,
        out_file="test_output.nii",
        mask_thresh=1.1,
        name="apply_mask_task"
    )    
)

###################
## WORKFLOW SETUP #
###################

wf.set_output(("output_img", wf.apply_mask_task.lzout.out_file))

# Execute the workflow (FastSurfer, siemans data)
result = wf(
    t1w="/Users/arkievdsouza/Desktop/ConnectomeBids/output/MRtrix3_connectome-participant_hcpmmp1/sub-01/scratch/freesurfer/mri/orig.mgz",
    mask="/Users/arkievdsouza/Desktop/ConnectomeBids/output/MRtrix3_connectome-participant_hcpmmp1/sub-01/scratch/freesurfer/mri/MASK_tmp.mgz",
    plugin="serial",
)

print("Result:", result)

