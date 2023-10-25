import os
import typing as ty
import pydra  
from pydra import Workflow, mark  
from pydra.engine.specs import File, Directory
from pydra.tasks.mrtrix3.v3_0 import fivett2vis, fivettgen_hsvs, labelconvert, labelsgmfix, mrconvert
from fileformats.medimage import NiftiGz, MghGz
from fileformats.medimage_mrtrix3 import ImageFormat
from pydra.tasks.fastsurfer.latest import fastsurfer
import shutil
from pathlib import Path
import shutil
from fileformats.generic import Directory
from fileformats.medimage import MghGz
from pydra import mark

# Define the path and output_path variables
# path = '/Users/arkievdsouza/Documents/NIFdata/ds000114'
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir'
mrtrix_lut_dir = '/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert'
freesurfer_home = '/Applications/freesurfer'
# Define the input_spec for the workflow
input_spec = {"t1w": NiftiGz, "fs_license": File, "sub_ID": str, "shared_parcellation": str, "FS_dir": str} 
output_spec = {"fTT_image": ImageFormat,"vis_image": ImageFormat,  "parc_image": ImageFormat}

# Create a workflow 
wf = Workflow(name='T1preproc_workflow', input_spec=input_spec, cache_dir=output_path, output_spec=output_spec) 

# # FastSurfer Task
# wf.add(
#     fastsurfer(
#         T1_files=wf.lzin.t1w, 
#         fs_license=wf.lzin.fs_license,
#         subject_id="FS_outputs",
#         name="FastSurfer_task",
#         py="python3.11",
#         norm_img="norm.mgz",
#         aparcaseg="aparcaseg.mgz",
#         # surf_only=True,
#         # seg=wf.lzin.segmentation,
#         # parallel=True,
#     )    
# )

# #################################################
# # Five Tissue Type Generation and visualisation #
# #################################################

# Five tissue-type task
wf.add(
    fivettgen_hsvs(
        input=wf.lzin.FS_dir, 
        output="fTT_hsvs.mif",
        name="fTTgen_task",
        nocrop=True,
        nocleanup=True,
        white_stem=True
    )
)

# Five tissue-type visualisation task
wf.add(
    fivett2vis(
        input=wf.fTTgen_task.lzout.output.cast(ImageFormat),
        output="fTT_hsvs_vis.mif",
        name="fTTvis_task"
    )
)

# ###############################
# # Generate parcellation image #
# ###############################
# parcellation="desikan"

# if parcellation == 'brainnetome246fs':
#     parc_lut_file = os.path.join(freesurfer_home,
#                                         'BN_Atlas_246_LUT.txt')
#     mrtrix_lut_file = ''
# elif parcellation == 'desikan':
#     parc_lut_file = os.path.join(freesurfer_home,
#                                         'FreeSurferColorLUT.txt')
#     mrtrix_lut_file = os.path.join(mrtrix_lut_dir,
#                                         'fs_default.txt')
# elif parcellation == 'destrieux':
#     parc_lut_file = os.path.join(freesurfer_home,
#                                         'FreeSurferColorLUT.txt')
#     mrtrix_lut_file = os.path.join(mrtrix_lut_dir,
#                                         'fs_a2009s.txt')
# elif parcellation == 'hcpmmp1':
#     parc_lut_file = os.path.join(mrtrix_lut_dir,
#                                         'hcpmmp1_original.txt')
#     mrtrix_lut_file = os.path.join(mrtrix_lut_dir,
#                                         'hcpmmp1_ordered.txt')
# elif parcellation in ['yeo7fs', 'yeo17fs']:
#     parc_lut_file = \
#         os.path.join(freesurfer_home,
#                         'Yeo2011_'
#                         + ('7' if parcellation == 'yeo7fs' else '17')
#                         + 'networks_Split_Components_LUT.txt')
#     mrtrix_lut_file = \
#         os.path.join(mrtrix_lut_dir,
#                         'Yeo2011_'
#                         + ('7' if parcellation == 'yeo7fs' else '17')
#                         + 'N_split.txt')

# # Grab the relevant parcellation image and target lookup table for conversion

# if wf.lzin.shared_parcellation == 'desikan':

    # parc_image_path = os.path.join(parc_image_path,
    #                                 'aparc+aseg.mgz')

    # Define a Pydra task for concatenating strings, thereby label the appropriate parcellation file
# Annotate the task
@mark.task
@mark.annotate(
    {"a": str}
)
def join_paths(a):
    p=os.path.join(a, 'mri')
    return p

# Add the task to the workflow
wf.add(join_paths(a=wf.lzin.FS_dir, name="join_task")) #CHANGE a TO BE OUTPUT FROM FASTSURFER_TASK
# Set the workflow output as the result of the join_task
wf.set_output(("parc_path_str", wf.join_task.lzout.out))

# elif shared.parcellation == 'destrieux':
#     parc_image_path = os.path.join(parc_image_path,
#                                            'aparc.a2009s+aseg.mgz')
#         # else:
#         #     # Non-standard parcellations are not applied as part of
#         #     #   the recon-all command; need to explicitly map them to
#         #     #   the subject
#         #     # This requires SUBJECTS_DIR to be set;
#         #     #   commands don't have a corresponding -sd option like recon-all
#         #     env = run.shared.env
#         #     env['SUBJECTS_DIR'] = app.SCRATCH_DIR
#         #     if shared.parcellation == 'brainnetome246fs':
#         #         for index, hemi in enumerate(['l', 'r']):
#         #             run.command(
#         #                 'mris_ca_label'
#         #                 + ' -l ' + os.path.join('freesurfer',
#         #                                         'label',
#         #                                         hemi + 'h.cortex.label')
#         #                 + ' freesurfer ' + hemi + 'h '
#         #                 + os.path.join('freesurfer',
#         #                                'surf',
#         #                                hemi + 'h.sphere.reg')
#         #                 + ' '
#         #                 + shared.brainnetome_cortex_gcs_paths[index]
#         #                 + ' '
#         #                 + os.path.join('freesurfer',
#         #                                'label',
#         #                                hemi + 'h.BN_Atlas.annot'),
#         #                 env=env)
#         #             run.command(
#         #                 'mri_label2vol'
#         #                 + ' --annot ' + os.path.join('freesurfer',
#         #                                              'label',
#         #                                              hemi + 'h.BN_Atlas.annot')
#         #                 + ' --temp ' + os.path.join('freesurfer',
#         #                                             'mri',
#         #                                             'brain.mgz')
#         #                 + ' --o ' + os.path.join('freesurfer',
#         #                                          'mri',
#         #                                          hemi + 'h.BN_Atlas.mgz')
#         #                 + ' --subject freesurfer'
#         #                 + ' --hemi ' + hemi + 'h'
#         #                 + ' --identity'
#         #                 + ' --proj frac 0 1 .1',
#         #                 env=env)
#         #         run.command(
#         #             'mri_ca_label '
#         #             + os.path.join('freesurfer',
#         #                            'mri',
#         #                            'brain.mgz')
#         #             + ' '
#         #             + os.path.join('freesurfer',
#         #                            'mri',
#         #                            'transforms',
#         #                            'talairach.m3z')
#         #             + ' '
#         #             + shared.brainnetome_sgm_gca_path
#         #             + ' '
#         #             + os.path.join('freesurfer',
#         #                            'mri',
#         #                            'BN_Atlas_subcortex.mgz'),
#         #             env=env)
#         #         parc_image_path = os.path.join(parc_image_path,
#         #                                        'aparc.BN_Atlas+aseg.mgz')
#         #         # Need to deal with prospect of overlapping mask labels
#         #         # - Any overlap between the two hemisphere ribbons
#         #         #   = set to zero
#         #         # - Any overlap between cortex and sub-cortical
#         #         #   = retain cortex
#         #         run.command('mrcalc '
#         #                     + ' '.join([os.path.join('freesurfer',
#         #                                              'mri',
#         #                                              hemi + 'h.BN_Atlas.mgz')
#         #                                 for hemi in ['l', 'r']])
#         #                     + ' -mult cortex_overlap.mif'
#         #                     + ' -datatype bit')
#         #         run.command('mrcalc '
#         #                     + ' '.join([os.path.join('freesurfer',
#         #                                              'mri',
#         #                                              hemi + 'h.BN_Atlas.mgz')
#         #                                 for hemi in ['l', 'r']])
#         #                     + ' -add '
#         #                     + os.path.join('freesurfer',
#         #                                    'mri',
#         #                                    'BN_Atlas_subcortex.mgz')
#         #                     + ' -mult sgm_overlap.mif'
#         #                     + ' -datatype bit')
#         #         run.command('mrcalc '
#         #                     + ' '.join([os.path.join('freesurfer',
#         #                                              'mri',
#         #                                              hemi + 'h.BN_Atlas.mgz')
#         #                                 for hemi in ['l', 'r']])
#         #                     + ' -add 1.0 cortex_overlap.mif -sub -mult '
#         #                     + os.path.join('freesurfer',
#         #                                    'mri',
#         #                                    'BN_Atlas_subcortex.mgz')
#         #                     + ' 1.0 sgm_overlap.mif -sub -mult -add '
#         #                     + parc_image_path)
#         #         app.cleanup('cortex_overlap.mif')
#         #         app.cleanup('sgm_overlap.mif')

#         #     elif shared.parcellation == 'hcpmmp1':
#         #         parc_image_path = os.path.join(parc_image_path,
#         #                                        'aparc.HCPMMP1+aseg.mgz')
#         #         for index, hemi in enumerate(['l', 'r']):
#         #             run.command('mri_surf2surf '
#         #                         '--srcsubject fsaverage '
#         #                         '--trgsubject freesurfer '
#         #                         '--hemi ' + hemi + 'h '
#         #                         '--sval-annot '
#         #                         + shared.hcpmmp1_annot_paths[index]
#         #                         + ' --tval '
#         #                         + os.path.join('freesurfer',
#         #                                        'label',
#         #                                        hemi + 'h.HCPMMP1.annot'),
#         #                         env=env)
#         #         run.command('mri_aparc2aseg '
#         #                     '--s freesurfer '
#         #                     '--old-ribbon '
#         #                     '--annot HCPMMP1 '
#         #                     '--o ' + parc_image_path,
#         #                     env=env)
#         #     elif shared.parcellation in ['yeo7fs', 'yeo17fs']:
#         #         num = '7' if shared.parcellation == 'yeo7fs' else '17'
#         #         parc_image_path = os.path.join(parc_image_path,
#         #                                        'aparc.Yeo' + num + '+aseg.mgz')
#         #         for index, hemi in enumerate(['l', 'r']):
#         #             run.command('mri_surf2surf '
#         #                         '--srcsubject fsaverage5 '
#         #                         '--trgsubject freesurfer '
#         #                         '--hemi ' + hemi + 'h '
#         #                         '--sval-annot ' + shared.yeo_annot_paths[index]
#         #                         + ' --tval '
#         #                         + os.path.join('freesurfer',
#         #                                        'label',
#         #                                        hemi + 'h.Yeo'
#         #                                        + num + '.annot'),
#         #                         env=env)
#         #         run.command('mri_aparc2aseg '
#         #                     '--s freesurfer '
#         #                     '--old-ribbon '
#         #                     '--annot Yeo' + num + ' '
#         #                     '--o ' + parc_image_path,
#         #                     env=env)
#         #     else:
#         #         assert False

# if shared.mrtrix_lut_file:
# # If necessary:
# # Perform the index conversion
# run.command('labelconvert ' + parc_image_path + ' '
#             + shared.parc_lut_file + ' '
#             + shared.mrtrix_lut_file
#             + ' parc_init.mif')
# # Fix the sub-cortical grey matter parcellations using FSL FIRST
# run.command('labelsgmfix parc_init.mif '
#             + freesurfer_T1w_input
#             + ' '
#             + shared.mrtrix_lut_file
#             + ' parc.mif')
# app.cleanup('parc_init.mif')
# else:
# # Non-standard sub-cortical parcellation;
# #   labelsgmfix not applicable
# run.command('mrconvert ' + parc_image_path + ' parc.mif '
#             '-datatype uint32')
# app.cleanup('freesurfer')


###################
## WORKFLOW SETUP #
###################

wf.set_output(("fTT_image", wf.fTTgen_task.lzout.output.cast(ImageFormat)))
wf.set_output(("vis_image", wf.fTTvis_task.lzout.output.cast(ImageFormat)))
wf.set_output(("parc_path_str", wf.join_task.lzout.out))
# wf.set_output(("parc_image", wf.SGMfix_task.lzout.output.cast(ImageFormat)))

# ## Execute the workflow (FastSurfer, NIF data)
# result = wf(
#     t1w="/Users/arkievdsouza/Documents/NIFdata/ds000114/sub-01/ses-retest/anat/sub-01_ses-retest_T1w.nii.gz",
#     fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
#     sub_ID="sub-01_ses-retest",
#     plugin="serial"
# )

# # Execute the workflow (FastSurfer, HCP data)
# result = wf(
#     t1w="/Users/arkievdsouza/Documents/100307/100307_FastSurfer/mri/orig.nii.gz",
#     fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
#     sub_ID="100307",
#     default_file="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/fs_default.txt",
#     freesurfer_LUT="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FreeSurferColorLUT.txt",
#     # segmentation="/Users/arkievdsouza/git/t1-pipeline/working-dir/fastsurfer_0425d50a2d1bdc642ef8feb235ec3855/subjects_dir/100307/mri/aparc.DKTatlas+aseg.deep.mgz",
#     plugin="serial",
# )

# Execute the workflow (FastSurfer, siemans data)
result = wf(
    t1w="/Users/arkievdsouza/Desktop/FastSurferTesting/data/sub-01_T1w_pos.nii.gz",
    fs_license="/Users/arkievdsouza/Desktop/FastSurferTesting/ReferenceFiles/FS_license.txt",
    sub_ID="sub-01",
    shared_parcellation="desikan", 
    plugin="serial",
    FS_dir="/Users/arkievdsouza/git/t1-pipeline/working-dir/fastsurfer_3af71ff49c76c541ad541bf24fd2849d/subjects_dir/FS_outputs/",
)

print("Result:", result)

