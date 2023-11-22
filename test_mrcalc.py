from pydra import Workflow
from pydra.tasks.mrtrix3.v3_0 import mrcalc

output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/brainnetome246fs_testing/'

# Define the mrcalc task
mrcalc_task = mrcalc(
    operand=['/Users/arkievdsouza/git/t1-pipeline/working-dir/brainnetome246fs_testing/sub-01/mri/lh.BN_Atlas.mgz', '/Users/arkievdsouza/git/t1-pipeline/working-dir/brainnetome246fs_testing/sub-01/mri/rh.BN_Atlas.mgz'],  # Pass the paths of the images as operands
    multiply=[True],  # Set the 'multiply' option to perform multiplication
    output_file='test.mif',  # Define the output path for the result
    name='mrcalc_task'  # Set a name for the task
)

# Create a Pydra workflow and add the mrcalc task to it
wf = Workflow(name="ImageMultiplicationWorkflow", cache_dir=output_path)
wf.add(mrcalc_task)

# Set the output of the workflow to the output of the mrcalc task
wf.set_output(("mrcalc_task", mrcalc_task.lzout.output_file))

# Run the workflow
wf_result = wf()
