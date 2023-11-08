from pydra import Workflow, mark
import os
import pydra.tasks.freesurfer.MRISurf2Surf
import pydra.tasks.freesurfer.MRIAparc2Aseg

# Define some filepaths
freesurfer_home='/Applications/freesurfer/'
mrtrix_lut_dir='/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert/' 
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/v2_tests/'

# Define the input values using input_spec
input_spec = {"FS_dir": str, "parcellation": str} 
wf = Workflow(name='hcpmmp1_parcellation', input_spec=input_spec,cache_dir=output_path) 

@mark.task
@mark.annotate({"parcellation": str, "FS_dir": str, "freesurfer_home": str,"return": {"fs_parc_image": str, "parc_lut_file": str, "mrtrix_lut_file": str, "output_parcellation_filename": str, "lh_white": str, "rh_white":str, "lh_pial": str, "rh_pial": str, "lh_ribbon": str, "rh_ribbon": str, "ribbon": str, "lh_annotation": str, "rh_annotation": str}})
def hcpmmp1_conversion(parcellation: str, FS_dir: str, freesurfer_home: str):
    if parcellation == 'hcpmmp1':
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
    return fs_parc_image, parc_lut_file, mrtrix_lut_file, output_parcellation_filename, lh_white, rh_white, lh_pial, rh_pial, lh_ribbon, rh_ribbon, ribbon, lh_annotation, rh_annotation

wf.add(
  aparc_2_aseg(
        name="aparc2aseg_task",
        subject_id="FS_outputs",
        out_file=output_parcellation_filename,
        lh_white=lh_white,
        rh_white=rh_white,
        lh_pial=lh_pial,
        rh_pial=rh_pial,
        lh_ribbon=lh_ribbon,
        rh_ribbon=rh_ribbon,
        ribbon=ribbon,
        lh_annotation=lh_annotation,
        rh_annotation=rh_annotation,
    )
)
  




    # elif shared.parcellation == 'hcpmmp1':
    #             parc_image_path = os.path.join(parc_image_path,
    #                                            'aparc.HCPMMP1+aseg.mgz')
    #             for index, hemi in enumerate(['l', 'r']):
    #                 run.command('mri_surf2surf '
    #                             '--srcsubject fsaverage '
    #                             '--trgsubject freesurfer '
    #                             '--hemi ' + hemi + 'h '
    #                             '--sval-annot '
    #                             + shared.hcpmmp1_annot_paths[index]
    #                             + ' --tval '
    #                             + os.path.join('freesurfer',
    #                                            'label',
    #                                            hemi + 'h.HCPMMP1.annot'),
    #                             env=env)
    #             run.command('mri_aparc2aseg '
    #                         '--s freesurfer '
    #                         '--old-ribbon '
    #                         '--annot HCPMMP1 '
    #                         '--o ' + parc_image_path,
    #                         env=env)


wf.add(hcpmmp1_conversion(parcellation=wf.lzin.parcellation, name="hcpmmp1_conversion_task"))


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
