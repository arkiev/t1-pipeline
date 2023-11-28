from pydra import Workflow, mark, ShellCommandTask
import os
from pydra.engine.specs import SpecInfo, BaseSpec, ShellSpec, ShellOutSpec
from pydra.tasks.mrtrix3.v3_0 import mask2glass
from fileformats.generic import File
import typing as ty

from pydra.tasks.mrtrix3.v3_0 import mask2glass

# Define the path and output_path variables
# path = '/Users/arkievdsouza/Documents/NIFdata/ds000114'
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/test_mask2glass/'

# Define the input_spec for the workflow
input_spec = {"input_mask": File} 
output_spec = {"glass_img": str}

# Create a workflow 
wf = Workflow(name='mask2glass_wf', input_spec=input_spec, cache_dir=output_path, output_spec=output_spec) 

wf.add(
    mask2glass(
        input=wf.lzin.input_mask,
        output="mask_glass.mif",
        name="mask2glass_task"
    )
    
)
########################
# Execute the workflow #
########################
wf.set_output(("mask2glass_task", wf.mask2glass_task.lzout.output))

result = wf(
    input_mask="/Users/arkievdsouza/git/t1-pipeline/working-dir/test_mask2glass/brain_mask.mgz",
    plugin="serial",
)

