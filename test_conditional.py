from pydra import mark, Workflow

# Define the input values using input_spec
input_spec = {"parcellation": str} 

# Create a Pydra Workflow
wf = Workflow(name='my_workflow', input_spec=input_spec) 

# Annotate the task
@mark.task
def conditional_task(parcellation: str):
    if parcellation == 'desikan':
        print("success!")

# Add the task to the workflow
wf.add(conditional_task(parcellation=wf.lzin.parcellation))

# Execute the workflow
result = wf(parcellation="desikan", plugin="serial")
print("Result:", result)
