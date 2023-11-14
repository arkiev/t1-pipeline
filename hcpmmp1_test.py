from pydra import Workflow, mark
import os
# from pydra.tasks.freesurfer import aparc_2_aseg
from pydra.tasks.freesurfer.auto import Aparc2Aseg
from pydra.tasks.freesurfer.v6 import MRISurf2Surf

# Define some filepaths
freesurfer_home='/Applications/freesurfer/'
mrtrix_lut_dir='/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert/' 
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/hcpmmp1_test/'
fsavg_dir= os.path.join(freesurfer_home,"subjects","fsaverage")
source_annotation_file_lh=os.path.join(fsavg_dir,'label','lh.HCPMMP1.annot')
source_annotation_file_rh=os.path.join(fsavg_dir,'label','rh.HCPMMP1.annot')
SUBJECT_DIR=''

# Define the input values using input_spec
input_spec = {"FS_dir": str, "parcellation": str} 
wf = Workflow(name='hcpmmp1_parcellation', input_spec=input_spec, cache_dir=output_path) 

@mark.task
@mark.annotate({"parcellation": str, "FS_dir": str, "freesurfer_home": str,"return": {"fs_parc_image": str, "parc_lut_file": str, "mrtrix_lut_file": str, "output_parcellation_filename": str, "lh_white": str, "rh_white":str, "lh_pial": str, "rh_pial": str, "lh_ribbon": str, "rh_ribbon": str, "ribbon": str, "lh_annotation": str, "rh_annotation": str}})
def join_hcpmmp1(parcellation: str, FS_dir: str, freesurfer_home: str):
    # if parcellation == 'hcpmmp1':
    fs_parc_image='N/A for this parcellation scheme'     
    parc_lut_file = os.path.join(mrtrix_lut_dir,'hcpmmp1_original.txt')
    mrtrix_lut_file = os.path.join(mrtrix_lut_dir,'hcpmmp1_ordered.txt')
    output_parcellation_filename ='aparc.HCPMMP1+aseg.mgz'
    lh_white= os.path.join(FS_dir,"surf","lh.white")
    rh_white= os.path.join(FS_dir,"surf","rh.white")
    lh_pial= os.path.join(FS_dir,"surf","lh.pial")
    rh_pial= os.path.join(FS_dir,"surf","rh.pial")
    lh_ribbon= os.path.join(FS_dir,"mri","lh.ribbon.mgz")
    rh_ribbon= os.path.join(FS_dir,"mri","rh.ribbon.mgz")
    ribbon= os.path.join(FS_dir,"mri","ribbon.mgz")
    lh_annotation= os.path.join(FS_dir,"label","lh.aparc.annot")
    rh_annotation= os.path.join(FS_dir,"label","rh.aparc.annot")
    print("FS_dir: ", FS_dir)
    print("parc_lut_file: ", parc_lut_file)
    print("lh_pial: ", lh_pial)
    print("lh_annotation: ", lh_annotation)    
    return fs_parc_image, parc_lut_file, mrtrix_lut_file, output_parcellation_filename, lh_white, rh_white, lh_pial, rh_pial, lh_ribbon, rh_ribbon, ribbon, lh_annotation, rh_annotation

wf.add(join_hcpmmp1(FS_dir=wf.lzin.FS_dir, parcellation=wf.lzin.parcellation, name="join_task_hcpmmp1"))

# Left hemisphere
wf.add(
  MRISurf2Surf(
        source_subject_id=fsavg_dir, #--srcsubject
        target_subject_id=wf.lzin.FS_dir, #--trgsubject
        source_annotation_file=source_annotation_file_lh, #--sval-annot
        target_annotation_file=wf.join_task_hcpmmp1.lzout.lh_annotation, #--tval
        hemisphere="lh", #--hemi
    )
)

wf.add(
  Aparc2Aseg(
        name="aparc2aseg_task",
        subject_id="FS_outputs",
        subjects_dir=wf.lzin.FS_dir,
        out_file=wf.join_task_hcpmmp1.lzout.output_parcellation_filename,
        lh_white=wf.join_task_hcpmmp1.lzout.lh_white,
        rh_white=wf.join_task_hcpmmp1.lzout.rh_white,
        lh_pial=wf.join_task_hcpmmp1.lzout.lh_pial,
        rh_pial=wf.join_task_hcpmmp1.lzout.rh_pial,
        lh_ribbon=wf.join_task_hcpmmp1.lzout.lh_ribbon,
        rh_ribbon=wf.join_task_hcpmmp1.lzout.rh_ribbon,
        ribbon=wf.join_task_hcpmmp1.lzout.ribbon,
        lh_annotation=wf.join_task_hcpmmp1.lzout.lh_annotation,
        rh_annotation=wf.join_task_hcpmmp1.lzout.rh_annotation,
        copy_inputs=True,
    )
)
  
########################
# Execute the workflow #
########################
# Set the workflow output as the result of the join_task
wf.set_output(("parcellation_image", wf.aparc2aseg_task.lzout.out_file))

result = wf(
    FS_dir="/Users/arkievdsouza/git/t1-pipeline/working-dir/fastsurfer_3af71ff49c76c541ad541bf24fd2849d/subjects_dir/FS_outputs/",
    parcellation="hcpmmp1",
    plugin="serial",
)
