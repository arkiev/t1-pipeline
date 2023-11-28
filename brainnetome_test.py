from pydra import Workflow, mark, ShellCommandTask
import os
from pydra.engine.specs import SpecInfo, BaseSpec, ShellSpec, ShellOutSpec
from pydra.tasks.freesurfer.auto import MRIsCALabel, Label2Vol, CALabel
from pydra.tasks.mrtrix3.v3_0 import mrcalc
from fileformats.generic import File
import typing as ty

# Define some filepaths
freesurfer_home='/Applications/freesurfer/'
mrtrix_lut_dir='/Users/arkievdsouza/git/mrtrix3/share/mrtrix3/labelconvert/' 
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir/brainnetome246fs_testing/'
os.environ["SUBJECTS_DIR"] = ''
# os.environ["PYTHONHASHSEED"] = ''
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
        transform=os.path.join(FS_dir,'mri','transforms','talairach.m3z')
        output_volume_calabel=os.path.join(FS_dir,'mri','BN_Atlas_subcortex.mgz')

        return output_parcellation_filename, parc_lut_file, brainnetome_gcs_path_lh, brainnetome_gcs_path_rh,brainnetome_sgm_gca_path ,lh_annotation , rh_annotation, sphere_file_lh, sphere_file_rh, cortex_label_lh, cortex_label_rh,template_volume, output_volume_l2v_lh, output_volume_l2v_rh, transform,output_volume_calabel

wf.add(join_task_brainnetome(FS_dir=wf.lzin.FS_dir, parcellation=wf.lzin.parcellation, freesurfer_home=freesurfer_home, name="join_task"))


# ######################
# # mriS_ca_label task #
# ######################
hemispheres = ['lh', 'rh']

for hemisphere in hemispheres:
    wf.add(
        MRIsCALabel(
            label=getattr(wf.join_task.lzout, f'cortex_label_{hemisphere}'),
            subject_id=wf.lzin.FS_dir,
            hemisphere=hemisphere,
            canonsurf=getattr(wf.join_task.lzout, f'sphere_file_{hemisphere}'),
            classifier=getattr(wf.join_task.lzout, f'brainnetome_gcs_path_{hemisphere}'),
            out_file=getattr(wf.join_task.lzout, f'{hemisphere}_annotation'),
            name=f'MRIsCAlabel_task_{hemisphere}'
        )
    )

######################
# mri_label2vol task #
######################
hemispheres = ['lh', 'rh']

for hemisphere in hemispheres:
    wf.add(
        Label2Vol(
            annot_file=getattr(wf, f"MRIsCAlabel_task_{hemisphere}").lzout.out_file,
            template_file=wf.join_task.lzout.template_volume,
            vol_label_file=getattr(wf.join_task.lzout, f"output_volume_l2v_{hemisphere}"),
            subject_id=wf.lzin.FS_dir,
            hemi=hemisphere,
            identity=True,
            proj='frac 0 1 .1',
            name=f'Label2Vol_task_{hemisphere}'
        )
    )


########################
# mri_ca_label task #
########################
wf.add(
    CALabel(
        in_file=wf.join_task.lzout.template_volume,
        out_file=wf.join_task.lzout.output_volume_calabel,
        transform=wf.join_task.lzout.transform,
        template=wf.join_task.lzout.brainnetome_sgm_gca_path,
        name='CALabel_task'

    )
)


######################################################################
#   # Need to deal with prospect of overlapping mask labels          #
    # - Any overlap between the two hemisphere ribbons = set to zero #
    # - Any overlap between cortex and sub-cortical = retain cortex  #
######################################################################

    # run.command('mrcalc '
    #             + ' '.join([os.path.join('freesurfer',
    #                                         'mri',
    #                                         hemi + 'h.BN_Atlas.mgz')
    #                         for hemi in ['l', 'r']])
    #             + ' -mult cortex_overlap.mif'
    #             + ' -datatype bit')
    # run.command('mrcalc '
    #             + ' '.join([os.path.join('freesurfer',
    #                                         'mri',
    #                                         hemi + 'h.BN_Atlas.mgz')
    #                         for hemi in ['l', 'r']])
    #             + ' -add '
    #             + os.path.join('freesurfer',
    #                             'mri',
    #                             'BN_Atlas_subcortex.mgz')
    #             + ' -mult sgm_overlap.mif'
    #             + ' -datatype bit')
    # run.command('mrcalc '
    #             + ' '.join([os.path.join('freesurfer',
    #                                         'mri',
    #                                         hemi + 'h.BN_Atlas.mgz')
    #                         for hemi in ['l', 'r']])
    #             + ' -add 1.0 cortex_overlap.mif -sub -mult '
    #             + os.path.join('freesurfer',
    #                             'mri',
    #                             'BN_Atlas_subcortex.mgz')
    #             + ' 1.0 sgm_overlap.mif -sub -mult -add '
    #             + parc_image_path)
    # app.cleanup('cortex_overlap.mif')
    # app.cleanup('sgm_overlap.mif')


########################
# Execute the workflow #
########################
wf.set_output(("CALabel_task", wf.CALabel_task.lzout.out_file))
wf.set_output(("MRIsCAlabel_task_lh", wf.MRIsCAlabel_task_lh.lzout.out_file))
wf.set_output(("MRIsCAlabel_task_rh", wf.MRIsCAlabel_task_rh.lzout.out_file))
wf.set_output(("Label2Vol_task_lh", wf.Label2Vol_task_lh.lzout.vol_label_file))
wf.set_output(("Label2Vol_task_rh", wf.Label2Vol_task_rh.lzout.vol_label_file))
# wf.set_output(("cortex_overlap_task", wf.cortex_overlap_task.lzout.out_image))

result = wf(
    FS_dir="/Users/arkievdsouza/git/t1-pipeline/working-dir/brainnetome246fs_testing/sub-01",
    parcellation="brainnetome246fs", 
    plugin="serial",
)


# LH RH iterations

# # ###########################
# # # mriS_ca_label task - lh #
# # ###########################
# wf.add(
#     MRIsCALabel(
#         label=wf.join_task.lzout.cortex_label_lh,
#         subject_id=wf.lzin.FS_dir,
#         hemisphere='lh',
#         canonsurf=wf.join_task.lzout.sphere_file_lh,
#         classifier=wf.join_task.lzout.brainnetome_gcs_path_lh,
#         out_file=wf.join_task.lzout.lh_annotation,
#         name='MRIsCAlabel_task_lh'
#     )
# )

# ###########################
# # mriS_ca_label task - rh #
# ###########################
# wf.add(
#     MRIsCALabel(
#         label=wf.join_task.lzout.cortex_label_rh,
#         subject_id=wf.lzin.FS_dir,
#         hemisphere='rh',
#         canonsurf=wf.join_task.lzout.sphere_file_rh,
#         classifier=wf.join_task.lzout.brainnetome_gcs_path_rh,
#         out_file=wf.join_task.lzout.rh_annotation,
#         name='MRIsCAlabel_task_rh'
#     )
# )


# ###########################
# # mri_label2vol task - lh #
# ###########################
# wf.add(
#     Label2Vol(
#         annot_file=wf.MRIsCAlabel_task_lh.lzout.out_file,
#         template_file=wf.join_task.lzout.template_volume,
#         vol_label_file=wf.join_task.lzout.output_volume_l2v_lh,
#         subject_id=wf.lzin.FS_dir,
#         hemi='lh',
#         identity=True,
#         proj='frac 0 1 .1',
#         name='Label2Vol_task_lh'
#     )
# )

# ###########################
# # mri_label2vol task - rh #
# ###########################
# wf.add(
#     Label2Vol(
#         annot_file=wf.MRIsCAlabel_task_rh.lzout.out_file,
#         template_file=wf.join_task.lzout.template_volume,
#         vol_label_file=wf.join_task.lzout.output_volume_l2v_rh,
#         subject_id=wf.lzin.FS_dir,
#         hemi='rh',
#         identity=True,
#         proj='frac 0 1 .1',
#         name='Label2Vol_task_rh'
#     )
# )