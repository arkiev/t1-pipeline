import os
import typing as ty
import pydra  
from pydra import Workflow, mark
from pydra.engine.specs import File
from pydra.tasks.mrtrix3.latest import fivetissuetypegen_hsvs, fivetissuetype2vis
from fileformats.generic import File
from pydra.tasks.fastsurfer.auto.fast_surfer import fast_surfer

from fileformats.medimage import NiftiGzXBvec, NiftiGz, MrtrixImage

# Define the path and output_path variables
path = '/Users/arkievdsouza/Documents/NIFdata/ds000114'
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir'

# Define the input_spec for the workflow
input_spec = {"t1w": NiftiGz}
output_spec = {"vis_image": MrtrixImage}

# Create a workflow 
wf = Workflow(name='T1preproc_workflow', input_spec=input_spec) 


# FastSurfer Task
wf.add(
    fast_surfer.fast_surfer(
        T1_files=wf.lzin.t1w, 
        subject_id=FastSurfer_outputs,
        subjects_dir=output_path,
        threads=24,
        parallel=True,
        name="FastSurfer_task"
    )    

)

#wf.set_output(("FastSurfer", wf.fTTgen_task.lzout.output))
wf.cache_dir = output_path 

# Execute the workflow
result = wf(
    t1w="/Users/arkievdsouza/Documents/NIFdata/ds000114/sub-01/ses-retest/anat/sub-01_ses-retest_T1w.nii.gz",
    plugin="serial",
)

print(f"Processed output generated at '{result.output.dwi_preproc}'")

# create_dotfile