from pydra import Workflow, mark, ShellCommandTask
import os
from pydra.engine.specs import SpecInfo, BaseSpec, ShellSpec, ShellOutSpec

# Define some filepaths
freesurfer_home='/Applications/freesurfer/'
mrtrix_lut_dir='/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert/' 
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/hcpmmp1_test/'
fsavg_dir= os.path.join(freesurfer_home,"subjects","fsaverage")
source_annotation_file_lh=os.path.join(fsavg_dir,'label','lh.HCPMMP1.annot')
source_annotation_file_rh=os.path.join(fsavg_dir,'label','rh.HCPMMP1.annot')
os.environ["SUBJECTS_DIR"] = ''
# print(os.environ)

# Define the input values using input_spec
input_spec = {"FS_dir": str, "parcellation": str} 
wf = Workflow(name='hcpmmp1_parcellation', input_spec=input_spec, cache_dir=output_path) 

@mark.task
@mark.annotate({"parcellation": str, "FS_dir": str, "freesurfer_home": str,"return": {"fs_parc_image": str, "parc_lut_file": str, "mrtrix_lut_file": str, "output_parcellation_filename": str,"lh_annotation": str,"rh_annotation": str}})
def join_hcpmmp1(parcellation: str, FS_dir: str, freesurfer_home: str):
    if parcellation == 'hcpmmp1':
        fs_parc_image='N/A for this parcellation scheme'     
        parc_lut_file = os.path.join(mrtrix_lut_dir,'hcpmmp1_original.txt')
        mrtrix_lut_file = os.path.join(mrtrix_lut_dir,'hcpmmp1_ordered.txt')
        output_parcellation_filename = os.path.join(FS_dir,"mri","'aparc.HCPMMP1+aseg.mgz'")
        lh_annotation= os.path.join(FS_dir,"label","lh.HCPMMP1.annot")
        rh_annotation= os.path.join(FS_dir,"label","rh.HCPMMP1.annot")
        print("lh_annotation: ", lh_annotation)
        return fs_parc_image,parc_lut_file,mrtrix_lut_file,output_parcellation_filename,lh_annotation,rh_annotation
wf.add(join_hcpmmp1(FS_dir=wf.lzin.FS_dir, parcellation=wf.lzin.parcellation, name="join_task_hcpmmp1"))

###########################
# mri_surf2surf spec info #
###########################

mri_s2s_input_spec = SpecInfo(
    name="Input",
    fields=[
    ( "source_subject_id", str,
      { "help_string": "source subject",
        "argstr": "--srcsubject",
        "mandatory": True } ),
    ( "target_subject_id", str,
      { "help_string": "target subject",
        "argstr": "--trgsubject",
        "mandatory": True } ),
    ( "source_annotation_file", str,
      { "help_string": "annotfile : map annotation",
        "argstr": "--sval-annot",
        "mandatory": True } ),
    ( "target_annotation_file", str,
      { "help_string": "path of file in which to store output values",
        "argstr": "--tval",
        "mandatory": True } ),
    ( "hemisphere", str,
      { "help_string": "hemisphere : (lh or rh) for both source and targ",
        "argstr": "--hemi",
        "mandatory": True } ),       
    ],
    bases=(ShellSpec,) 
)

mri_s2s_output_spec=SpecInfo(
    name="Output",
    fields=[
    ( "target_annotation_file", str,
      { "help_string": "path of file in which to store output values",
        "argstr": "--tval",
        "mandatory": True } ),
    ],
    bases=(ShellOutSpec,) 
)

###########################
# mri_surf2surf task - lh #
###########################

wf.add(
    ShellCommandTask(
        name="mri_s2s_task_lh",
        executable="mri_surf2surf",
        input_spec=mri_s2s_input_spec, 
        output_spec=mri_s2s_output_spec, 
        cache_dir=output_path,
        source_subject_id=fsavg_dir,
        target_subject_id=wf.lzin.FS_dir,
        source_annotation_file=source_annotation_file_lh,
        target_annotation_file=wf.join_task_hcpmmp1.lzout.lh_annotation, 
        hemisphere="lh",      
    )
)

###########################
# mri_surf2surf task - rh #     Update this to be a loop for hemisphere  (lh and rh)
###########################

wf.add(
    ShellCommandTask(
        name="mri_s2s_task_rh",
        executable="mri_surf2surf",
        input_spec=mri_s2s_input_spec, 
        output_spec=mri_s2s_output_spec, 
        cache_dir=output_path,
        source_subject_id=fsavg_dir,
        target_subject_id=wf.lzin.FS_dir,
        source_annotation_file=source_annotation_file_rh,
        target_annotation_file=wf.join_task_hcpmmp1.lzout.rh_annotation, 
        hemisphere="rh",      
    )
)

# ############################
# # mri_aparc2aseg spec info #
# ############################

mri_a2a_input_spec = SpecInfo(
    name="Input",
    fields=[
    ( "subject", str,
      { "help_string": "Name of the subject as found in the SUBJECTS_DIR",
        "argstr": "--s",
        "mandatory": True } ),
    ( "old_ribbon", bool,
      { "help_string": "use mri/hemi.ribbon.mgz as a mask for the cortex",
        "argstr": "--old-ribbon",
        "mandatory": True } ),
    ( "annotname", str,
      { "help_string": "Use annotname surface annotation. By default, uses ?h.aparc.annot. With this option, it will load ?h.annotname.annot. The output file will be set to annotname+aseg.mgz, but this can be changed with --o. Note: running --annot aparc.a2009s is NOT the same as running --a2009s. The index numbers will be different.",
		"argstr": "--annot",
        "mandatory": True } ),
    ( "volfile", str,
      { "help_string": "Full path of file to save the output segmentation in. Default is mri/aparc+aseg.mgz",
        "argstr": "--o",
        "mandatory": True } ),    
    ],
    bases=(ShellSpec,) 
)

mri_a2a_output_spec=SpecInfo(
    name="Output",
    fields=[
    ( "volfile", str,
      { "help_string": "Full path of file to save the output segmentation in. Default is mri/aparc+aseg.mgz",
        "argstr": "--o",
        "mandatory": True } ),
    ],
    bases=(ShellOutSpec,) 
)

# #######################
# # mri_aparc2aseg task #
# #######################

wf.add(
    ShellCommandTask(
        name="mri_a2a_task",
        executable="mri_aparc2aseg",
        input_spec=mri_a2a_input_spec, 
        output_spec=mri_a2a_output_spec, 
        cache_dir=output_path,
        subject=wf.lzin.FS_dir,
        old_ribbon=True,
        annotname="HCPMMP1",
        volfile=wf.join_task_hcpmmp1.lzout.output_parcellation_filename,
    )
)
  
########################
# Execute the workflow #
########################
# Set the workflow output as the result of the join_task
# wf.set_output(("parcellation_image", wf.aparc2aseg_task.lzout.out_file))
wf.set_output(("aparc_aseg_HCPMMP1", wf.mri_a2a_task.lzout.volfile))
wf.set_output(("annot_lh", wf.mri_s2s_task_lh.lzout.target_annotation_file))
wf.set_output(("annot_rh", wf.mri_s2s_task_rh.lzout.target_annotation_file))

result = wf(
    FS_dir="/Users/arkievdsouza/git/t1-pipeline/working-dir/hcpmmp1_test/100307_orig",
    parcellation="hcpmmp1",
    plugin="serial",
)
