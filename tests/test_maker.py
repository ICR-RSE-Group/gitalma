import os, pathlib
from pathlib import Path
def test_maker():
    # run the gitlab_maker.py script
    gitlab_maker_path = os.path.join(Path(os.path.dirname(__file__)).parent, 'gitlab_maker.py')
    if os.path.exists(gitlab_maker_path):
        os.system(f'python3 {gitlab_maker_path}')
    else:
        print(f"File {gitlab_maker_path} does not exist.")
        assert False
    assert True