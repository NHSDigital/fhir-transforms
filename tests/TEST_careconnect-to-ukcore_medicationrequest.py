import pytest, os
from lib import common

## Location of input and maps files for CareConnect MedicationRequest
base_path = '../resources/careconnect-to-ukcore/medicationrequest/'
input_files = next(os.walk(base_path + 'input'), (None, None, []))[2]

@pytest.mark.parametrize('input_file', input_files)
def test_transforms(input_file):
    # Run transform
    common.call_validator_cli(input_file, base_path)
    assert os.path.exists('/tmp/expected-' + input_file) 

    [transformed, expected] = common.sort_json_files(input_file, base_path)
    common.remove_files(['/tmp/expected-' + input_file])      # Clean up transformed file

    # Test transformed matches expected
    assert transformed == expected
