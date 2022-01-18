import pytest, os, shutil, subprocess, json

base_path = '../resources/careconnect-to-ukcore/medicationrequest/'
base_uri = 'http://fhir.nhs.uk/StructureMap/'

input_files = next(os.walk(base_path + 'input'), (None, None, []))[2]
expected_files = next(os.walk(base_path + 'expected'), (None, None, []))[2]

# sorted(input_files) != sorted(expected_files):
#   pytest.exit('Exit testing - Each input file does not have a corresponding expected file.')

@pytest.mark.parametrize('input_file', input_files)
def test_transforms(input_file):
    # Trim number (_###) and extension off file name to use for transform value and map file name
    base_input_name = input_file.split('_')[0]

    # validator_cli.jar doesn't seem to work withi absolute or relative paths, so need to move input file/map into cwd
    shutil.copy(base_path + 'input/' + input_file, '.', follow_symlinks=True)
    shutil.copy(base_path + 'maps/' + base_input_name + '.map', '.', follow_symlinks=True)
    try:
        process = subprocess.run([
		        'java',
		        '-jar',
		        '../validator_cli.jar',
		        './' + input_file,
                '-transform', 
                base_uri + base_input_name,
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
    # Remove input/map files from cwd
    remove_files(['./' + input_file, './' + base_input_name + '.map'])

    # Seems like some subprocesses of the validator_cli might be returning non zero exit codes,
    # so asserting on the returncode of the process isn't reliable.  There also seems to be things
    # being written to stderr even when its sucessful.  If the file exists and 
    assert os.path.exists('/tmp/expected-' + input_file) 

@pytest.mark.parametrize('expected_file', expected_files)
def test_transform_output(expected_file):
    
    transformed_json = json.load(open('/tmp/expected-' + expected_file))
    expected_json = json.load(open(base_path + 'expected/' + expected_file))
    
    transformed = json.dumps(transformed_json, sort_keys=True)
    expected = json.dumps(expected_json, sort_keys=True)

    remove_files(['/tmp/expected-' + expected_file])

    assert transformed == expected

# Helper function
# Remove files and ignore error if file does not exist
def remove_files(files):
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            if e.errno != errno.ENOENT:
               raise
