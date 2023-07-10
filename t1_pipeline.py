
###################
# modules to load #
###################

import nipype.interfaces.io as nio  # Data i/o
import nipype.interfaces.utility as util  # utility
import nipype.pipeline.engine as pe  # pypeline engine
import nipype.interfaces.mrtrix3 as mrtrix  # <---- The important new part!
import nipype.interfaces.fsl as fsl
import nipype.interfaces.freesurfer as freesurfer  
import nipype.algorithms.misc as misc

from nipype import DataGrabber, Node
from nipype import SelectFiles, Node
from nipype.interfaces.io import DataSink

import os
import os.path as op  # system functions

###############
# Defintiions #
###############

path = '/Users/arkievdsouza/Documents/NIFdata'
output_path = '/Users/arkievdsouza/git/t1-pipeline/working-dir'
# subject_list = [1, 2]
# session_list = ['retest', 'test']
subject_list = [1]
session_list = ['retest']


# source subjects and sessions
infosource = pe.Node(
    interface=util.IdentityInterface(fields=['subject_id', 'session_id']),
    name="infosource_SelectImages")
infosource.iterables = [('subject_id', subject_list), ('session_id', session_list)]
infosource.output = ['subject_id', 'session_id']

###############################################
# datagrabber node to locate anatomical image #
###############################################

# define datagrabber for images
dg = Node(DataGrabber(infields=['subject_id', 'session_id'],
                      outfields=['anat']),
          name='datagrabber_SubjectAnatImages')

# Location of the dataset folder
dg.inputs.base_directory = path
# Necessary default parameters
dg.inputs.template = '*'
dg.inputs.sort_filelist = True
# Specify the datagrabber templates
dg.inputs.template_args = {'anat': [['subject_id', 'session_id']]}
dg.inputs.field_template = {'anat': 'sub-%02d/ses-%s/anat/*_T1w.nii.gz'}

##################
# recon-all node #
##################

from nipype.interfaces.freesurfer import ReconAll

# Create Node
RA_node = Node(ReconAll(), name='ReconAll')
# Specify node inputs
RA_node.inputs.subject_id = 'ReconAllOutputs'
RA_node.inputs.directive = 'all'
RA_node.inputs.subjects_dir = '.'
RA_node.inputs.openmp = 8
RA_node.inputs.parallel = True

###############################################
# intermediate node to create recon_directory #
###############################################

from nipype.interfaces.utility import Function

def concatenate_paths(subjects_dir):
    import os
    return os.path.join(subjects_dir, 'ReconAllOutputs')

concatenate_paths_node = Node(
    Function(
        input_names=['subjects_dir'],
        output_names=['recon_directory'],
        function=concatenate_paths
    ),
    name='concatenate_paths_node'
)

###############
# 5TTgen node #
###############

# mrt.Generate5tt does not have hsvs, so let's try make hsvs run using commandline interface

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, Directory, TraitedSpec, File

class CustomHSVSInputSpec(CommandLineInputSpec):
    in_dir = Directory(exists=True, mandatory=True, argstr='%s', position=0, desc='the input recon-all subject directory')

    # Do not set exists=True for output files!
    out_file = File(mandatory=True, argstr='%s', position=1, desc='the output 5TThsvs image')
class CustomHSVSOutputSpec(TraitedSpec):
    out_file = File(desc='the output 5TThsvs image')


class CustomHSVS(CommandLine):
    _cmd = '5ttgen hsvs -scratch . '
    input_spec = CustomHSVSInputSpec
    output_spec = CustomHSVSOutputSpec

    def _list_outputs(self):
        # Get the attribute saved during _run_interface
        return {'out_file': self.inputs.out_file}

fTT_node = Node(CustomHSVS(out_file='fTThsvs.mif.gz'), name='5ttgenHSVS')

###############
# 5TTvis node #
###############

# mrtrix module does not have 5tt2vis so let's try make hsvs run using commandline interface

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, Directory, TraitedSpec, File

class CustomHSVS2visInputSpec(CommandLineInputSpec):
    in_file = File(exists=True, mandatory=True, argstr='%s', position=0, desc='the 5-volume 5TT image')

#     # Do not set exists=True for output files!
    out_file = File(mandatory=True, argstr='%s', position=1, desc='the single-volume 5TTvis image')

class CustomHSVS2visOutputSpec(TraitedSpec):
    out_file = File(mandatory=True, argstr='%s', position=1, desc='the 5-volume 5TT image')

class CustomHSVS2vis(CommandLine):
    _cmd = '5tt2vis'
    input_spec = CustomHSVS2visInputSpec
    output_spec = CustomHSVS2visOutputSpec

    def _list_outputs(self):
        # Get the attribute saved during _run_interface
        return {'out_file': self.inputs.out_file}
    
fTT2vis_node = Node(CustomHSVS2vis(out_file='fTThsvs_vis.mif.gz'), name='5tt2vis')

#######################################
# Create a data-sink to store outputs #
#######################################

from nipype.interfaces.io import DataSink

# Create DataSink object
sinker = Node(DataSink(), name='sinker')

# Name of the output folder
sinker.inputs.base_directory =  os.path.join(output_path, 'T1_processing_pipeline')

#################
# connect nodes #
#################

T1pipline_wf = pe.Workflow(name="T1_processing_pipeline")
T1pipline_wf.base_dir = os.path.abspath(output_path)
T1pipline_wf.connect([(infosource, dg, [('subject_id', 'subject_id'),
                                   ('session_id', 'session_id')])])
T1pipline_wf.connect([(dg, RA_node, [('anat', 'T1_files')])])

T1pipline_wf.connect([(RA_node, concatenate_paths_node, [('subjects_dir', 'subjects_dir')])])
T1pipline_wf.connect([(concatenate_paths_node, fTT_node, [('recon_directory', 'in_dir')])])
T1pipline_wf.connect([(fTT_node, fTT2vis_node, [('out_file', 'in_file')])])

# Connect DataSink with the relevant nodes
T1pipline_wf.connect([(fTT2vis_node, sinker, [('out_file', 'vis_image')]),
            (fTT_node, sinker, [('out_file', 'fTT_image')])])


# Connect DataSink with the relevant nodes
T1pipline_wf.write_graph(graph2use='exec')
T1pipline_wf.config['execution']['remove_unnecessary_outputs'] = False

result = T1pipline_wf.run()


