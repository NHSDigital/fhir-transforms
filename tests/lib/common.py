import os, shutil, subprocess, json

## Base URI
#  This is the base URI to use for NHSD identities, which should be common (I think...)
BASE_URI = 'http://fhir.nhs.uk/StructureMap/'

## @package common
#  Helper and common functions for tests

## Common function for tests to call the validator_cli.  If running locally, 
#  download the validator_cli.jar from 
#  https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar 
#  and place in the root of the repo.
#
#  @param input_file The filename of the input file to be transformed
#  @param base_path  The path of a particular set of FHIR content to transform,
#                    naming conventions must be followed for paths and filenames.
#                    See ./README.md for more details.
#  @return void - A file will be written in temp if this completes sucessfully, 
#                 the test should check the existence of this, if an exception was raised
#                 it should not exist. Doesn't seem to be a tidier way of doing this...
def call_validator_cli(input_file, base_path):
    # Trim number (_###) and extension off file name to use for transform value and map file name
    base_input_name = input_file.split('_')[0]

    # The validator_cli.jar doesn't seem to work withi absolute or relative paths, 
    # so need to move input file/map into cwd.  Files are cleaned up aferwards
    shutil.copy(base_path + 'input/' + input_file, '.', follow_symlinks=True)
    shutil.copy(base_path + 'maps/' + base_input_name + '.map', '.', follow_symlinks=True)
    try:
        process = subprocess.run([
                'java',
                '-jar',
                '../validator_cli.jar',
                './' + input_file,
                '-transform',
                BASE_URI + base_input_name,
                '-version',
                '4.0.1',
                '-ig',
                './' + base_input_name + '.map',
                '-output',
                '/tmp/expected-' + input_file
        ],
        check=True,
        stderr=subprocess.PIPE
        )
    except:
        remove_files(['./' + input_file, './' + base_input_name + '.map'])
    remove_files(['./' + input_file, './' + base_input_name + '.map'])

## Helper function to sort the transformed files and the expected output.
#  @param input_file The name of the input file, which will be used to 
#                    name the transformed file and retrieve the expected
#                    file.  See ./README.md for details.
#  @base_path        The path of the specific set of FHIR to transform
#  @return           The sorted versions of the transformed and expected
#                    json.
def sort_json_files(input_file, base_path):
    transformed_json = json.load(open('/tmp/expected-' + input_file))
    expected_json = json.load(open(base_path + 'expected/' + input_file))

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
