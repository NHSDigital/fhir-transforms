import os, shutil, subprocess, json, errno

## @package common
#  Helper and common functions for tests

## Base URI
#  This is the base URI to use for NHSD identities, which should be common (I think...)
BASE_URI = 'http://fhir.nhs.uk/StructureMap/'

## Base Path
#  Location of input, expected and map files
BASE_PATH = '../resources'

## Helper function for fetching the input files.  
#  Maybe look at fixtures if the reporting isn't clear enough
def get_input_files():
   input_files = []
   for project in filter(os.path.isdir, [os.path.join(BASE_PATH, f) for f in os.listdir(BASE_PATH)]):
       for resource in filter(os.path.isdir, [os.path.join(project, f) for f in os.listdir(project)]):
           base_path = resource + '/input/'
           input_files.extend([base_path + filename
                               for filename in os.listdir(base_path)
                               if os.path.isfile(base_path + filename)
                               if not filename.startswith('.')])
   return input_files

## Common function for tests to call the validator_cli.  If running locally, 
#  download the validator_cli.jar from 
#  https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar 
#  and place in the root of the repo.
#
#  @param input_file The path of the input file to be transformed
#  @return void - A file will be written in temp if this completes sucessfully, 
#                 the test should check the existence of this, if an exception was raised
#                 it should not exist. Doesn't seem to be a tidier way of doing this...
def call_validator_cli(input_file):
    # Get just the filename and the base path of the input folder, as this
    # will be used to fetch the map files.
    base_path = os.path.dirname(input_file).rsplit('/', 1)[0]
    base_input_file_name = os.path.basename(input_file)

    # Trim number (_###) and extension off file name to use for transform value and map file name
    base_input_name = base_input_file_name.split('_')[0]

    # The validator_cli.jar doesn't seem to work withi absolute or relative paths, 
    # so need to move input file/map into cwd.  Files are cleaned up aferwards
    shutil.copy(input_file, '.', follow_symlinks=True)
    shutil.copy(base_path + '/maps/' + base_input_name + '.map', '.', follow_symlinks=True)
    try:
        process = subprocess.run([
                'java',
                '-jar',
                '../validator_cli.jar',
                './' + base_input_file_name,
                '-transform',
                BASE_URI + base_input_name,
                '-ig',
                './' + base_input_name + '.map',
                '-output',
                '/tmp/expected-' + base_input_file_name
        ],
        check=True,
        stderr=subprocess.PIPE
        )
    except:
        remove_files(['./' + base_input_file_name, './' + base_input_name + '.map'])
    remove_files(['./' + base_input_file_name, './' + base_input_name + '.map'])

## Helper function to sort the transformed files and the expected output.
#  @param input_file The path of the input file, the base of which will 
#                    be used to name the transformed file and retrieve 
#                    the expected file.  See ./README.md for details.
#  @return           The sorted versions of the transformed and expected
#                    json.
def sort_json_files(input_file):
    # Get just the filename and the base path of the input folder, as this
    # will be used to fetch the expected files.
    base_input_file_name = os.path.basename(input_file)
    base_path = os.path.dirname(input_file).rsplit('/', 1)[0]

    transformed_json = json.load(open('/tmp/expected-' + base_input_file_name))
    expected_json = json.load(open(base_path + '/expected/' + base_input_file_name))

    transformed = json.dumps(transformed_json, sort_keys=True)
    expected = json.dumps(expected_json, sort_keys=True)

    return [transformed, expected]

## Helper function to remove files and ignore error if file does not exist
#  @param files List of files to remove
def remove_files(files):
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            if e.errno != errno.ENOENT:
               raise
