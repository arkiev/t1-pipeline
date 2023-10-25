from pydra import mark, Workflow
import os

# Define the input values using input_spec
input_spec = {"FS_dir": str, "parcellation": str} 

# Create a Pydra Workflow
wf = Workflow(name='my_workflow', input_spec=input_spec) 

# Annotate the task
@mark.task
def identify_parc(parcellation: str):
    if parcellation == 'desikan':
        print("Parcellation type: ", parcellation)
        parc_image="aparc+aseg.mgz"
        return parc_image
    
# Add the task to the workflow
wf.add(identify_parc(parcellation=wf.lzin.parcellation, name="identifyparc_task"))
wf.set_output(("output_identify_parc", wf.identifyparc_task.lzout.out))

# Annotate the task
@mark.task
def join_paths(fs_dir: str, parc_image: str) -> str:
    p=os.path.join(fs_dir, 'mri', parc_image)
    return p
# Add the task to the workflow
wf.add(join_paths(fs_dir=wf.lzin.FS_dir, parc_image=wf.identifyparc_task.lzout.out, name="join_task"))
# Set the workflow output as the result of the join_task
wf.set_output(("myoutput", wf.join_task.lzout.out))

# Execute the workflow
result = wf(
    FS_dir="/Users/arkievdsouza/git/t1-pipeline/working-dir/fastsurfer_3af71ff49c76c541ad541bf24fd2849d/subjects_dir/FS_outputs/",
    parcellation="desikan",
    plugin="serial",
)
print("Result:", result)


# # Annotate the task
# @mark.task
# # @mark.annotate(
# #     {"a": str, "return": {"p": str}}
# # )
# def join_paths(a: str) -> str:
#     p=os.path.join(a, 'mri/aparc.a2009s+aseg.mgz')
#     return p
