import os
import typing as ty
import pydra  
from pydra import Workflow, mark
from pydra.engine.specs import File
# from pydra.tasks.mrtrix3.latest import fivetissuetypegen_hsvs, fivetissuetype2vis
from pydra.tasks.fastsurfer.latest import fastsurfer
from fileformats.generic import File, Directory
from fileformats.medimage import NiftiGzXBvec, NiftiGz
from pathlib import Path

# Define the path and output_path variables
path = '/Users/arkievdsouza/Documents/NIFdata/ds000114'
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir'

# Define the input_spec for the workflow
input_spec = {"t1w": NiftiGz, "fs_license": File}
# output_spec = ["output_FS"]  # : Directory}
output_spec = {"output_FS": Directory}

# Create a workflow 
wf = Workflow(name='FastSurferTest', input_spec=input_spec, cache_dir=output_path, output_spec=output_spec) 

# FastSurfer Task
wf.add(
    fastsurfer(
        T1_files=wf.lzin.t1w, 
        fs_license=wf.lzin.fs_license,
        subjects_dir=output_path,
        subject_id="FastSurfer_outputs",
        threads=24,
        parallel=True,
        name="FastSurfer_task",
        seg_only=True,
        py="python3.11",
        no_cuda=True
        # container_info=('docker','deepmi/fastsurfer:latest')
    )    

)

# FS_output_path=output_path+"/FastSurfer_outputs/"
FS_output_path=Path(output_path+"/FastSurfer_outputs/")
print(FS_output_path, type(FS_output_path))

wf.set_output(("output_FS", FS_output_path))



# Execute the workflow
result = wf(
    t1w="/Users/arkievdsouza/Documents/NIFdata/ds000114/sub-01/ses-retest/anat/sub-01_ses-retest_T1w.nii.gz",
    fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
    plugin="serial"
)

# print(f"Processed output generated at '{result.output.dwi_preproc}'")

# create_dotfile