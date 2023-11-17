from pydra import Workflow, mark, ShellCommandTask
import os
from pydra.engine.specs import SpecInfo, BaseSpec, ShellSpec, ShellOutSpec

# Define some filepaths
freesurfer_home='/Applications/freesurfer/'
mrtrix_lut_dir='/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert/' 
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/brainnetome246fs_testing/'
os.environ["SUBJECTS_DIR"] = ''

# Define the input values using input_spec
input_spec = {"FS_dir": str, "parcellation": str} 
wf = Workflow(name='brainnetome_parcellation', input_spec=input_spec, cache_dir=output_path) 

@mark.task
@mark.annotate({
    "parcellation": str,
    "FS_dir": str,
    "freesurfer_home": str,
    "return": {
        "output_parcellation_filename": str,
        "parc_lut_file": str,
        "brainnetome_gcs_path_lh": str,
        "brainnetome_gcs_path_rh": str,
        "brainnetome_sgm_gca_path": str,
        "lh_annotation": str,
        "rh_annotation": str,
        "sphere_file_lh": str,
        "sphere_file_rh": str,
        "cortex_label_lh": str,
        "cortex_label_rh": str,
        "template_volume": str,
        "output_volume_l2v_lh": str,
        "output_volume_l2v_rh": str,
        "transform": str,
        "output_volume_calabel": str,
    }
})
def join_task_brainnetome(parcellation: str, FS_dir: str, freesurfer_home: str):
    if parcellation == 'brainnetome246fs':
        # brainnetome definitions
        #fsavg_dir=#os.path.join(freesurfer_home,"subjects","fsaverage") 
        #mrtrix_lut_file = #os.path.join(mrtrix_lut_dir,'hcpmmp1_ordered.txt')
        output_parcellation_filename = os.path.join(FS_dir,"mri","aparc.BN_Atlas+aseg.mgz")
        parc_lut_file = os.path.join(freesurfer_home,'brainnetome','BN_Atlas_246_LUT.txt')
        brainnetome_gcs_path_lh=os.path.join(freesurfer_home,'average','lh.BN_Atlas.gcs')
        brainnetome_gcs_path_rh=os.path.join(freesurfer_home,'average','rh.BN_Atlas.gcs')
        brainnetome_sgm_gca_path=os.path.join(freesurfer_home,'average','BN_Atlas_subcortex.gca')
        lh_annotation= os.path.join(FS_dir,"label","lh.BN_Atlas.annot")
        rh_annotation= os.path.join(FS_dir,"label","rh.BN_Atlas.annot")
        sphere_file_lh=os.path.join(FS_dir,'surf','lh.sphere.reg')
        sphere_file_rh=os.path.join(FS_dir,'surf','rh.sphere.reg')
        cortex_label_lh=os.path.join(FS_dir,'label','lh.cortex.label')
        cortex_label_rh=os.path.join(FS_dir,'label','rh.cortex.label')
        template_volume=os.path.join(FS_dir,'mri','brain.mgz')
        output_volume_l2v_lh=os.path.join(FS_dir,'mri','lh.BN_Atlas.mgz')
        output_volume_l2v_rh=os.path.join(FS_dir,'mri','rh.BN_Atlas.mgz')
        transform=os.path.join(FS_dir,'transforms','talairach.m3z')
        output_volume_calabel=os.path.join(FS_dir,'mri','rh.BN_Atlas.mgz')

        return output_parcellation_filename, parc_lut_file, brainnetome_gcs_path_lh, brainnetome_gcs_path_rh,brainnetome_sgm_gca_path ,lh_annotation , lh_annotation, rh_annotation, sphere_file_lh, sphere_file_rh, cortex_label_lh, cortex_label_rh,template_volume, output_volume_l2v_lh, output_volume_l2v_rh, transform,output_volume_calabel

wf.add(join_task_brainnetome(FS_dir=wf.lzin.FS_dir, parcellation=wf.lzin.parcellation, freesurfer_home=freesurfer_home, name="join_task"))


###########################
# mri_surf2surf spec info #
###########################

mris_calabel_input_spec = SpecInfo(
    name="Input",
    fields=[
    ( "l_option", str,
      { "help_string": "<unknown>",
        "argstr": "-l",
        "mandatory": True },
        "position " ),
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
        source_subject_id=wf.join_task.lzout.fsavg_dir,
        target_subject_id=wf.lzin.FS_dir,
        source_annotation_file=wf.join_task.lzout.source_annotation_file_lh,
        target_annotation_file=wf.join_task.lzout.lh_annotation, 
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
        source_subject_id=wf.join_task.lzout.fsavg_dir,
        target_subject_id=wf.lzin.FS_dir,
        source_annotation_file=wf.join_task.lzout.source_annotation_file_rh,
        target_annotation_file=wf.join_task.lzout.rh_annotation, 
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

# ########################
# # mri_aparc2aseg task  #
# ########################

wf.add(
    ShellCommandTask(
        name="mri_a2a_task",
        executable="mri_aparc2aseg",
        input_spec=mri_a2a_input_spec, 
        output_spec=mri_a2a_output_spec, 
        cache_dir=output_path,
        subject=wf.lzin.FS_dir,
        old_ribbon=True,
        annotname=wf.lzin.parcellation,
        volfile=wf.join_task.lzout.output_parcellation_filename,
    )
)
  
########################
# Execute the workflow #
########################
# Set the workflow output as the result of the join_task
# wf.set_output(("parcellation_image", wf.aparc2aseg_task.lzout.out_file))
wf.set_output(("aparc_aseg", wf.mri_a2a_task.lzout.volfile))
wf.set_output(("annot_lh", wf.mri_s2s_task_lh.lzout.target_annotation_file))
wf.set_output(("annot_rh", wf.mri_s2s_task_rh.lzout.target_annotation_file))

result = wf(
    FS_dir="/Users/arkievdsouza/git/t1-pipeline/working-dir/brainnetome246fs_testing/sub-01",
    parcellation="brainnetome246fs", #yeo7fs  yeo17fs yeo7fs
    plugin="serial",
)
