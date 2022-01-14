import pytest, os
from lib import common

input_files = common.get_input_files()

@pytest.mark.parametrize('input_file', input_files)
def test_transforms(input_file):
    # Get base filename
    base_input_file_name = os.path.basename(input_file)

    # Run transform
    common.call_validator_cli(input_file)
    assert os.path.exists('/tmp/expected-' + base_input_file_name) 

    [transformed, expected] = common.sort_json_files(input_file)
    common.remove_files(['/tmp/expected-' + base_input_file_name])      # Clean up transformed file

    # Test transformed matches expected
    assert transformed == expected
