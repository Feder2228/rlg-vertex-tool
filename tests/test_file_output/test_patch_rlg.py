import unittest
from src.rlgtool import rlgtool
from src.rlgtool import nlgutil
from src.rlgtool import util
from src.rlgtool import rlg_data_structures


class TestPatchRlg(unittest.TestCase):
    """Tests for the patch rlg command
    Analyzes the newly created rlg file
    """
    def test_add_models_to_root(self):
        rlgtool.generate_rlg_from_rlg_and_dae(srcrlgpath='./tests/test_files/mario.rlg', 
                                              dstrlgpath='./tests/test_files/new.rlg',
                                              daepath='./tests/test_files/correct_file.dae')