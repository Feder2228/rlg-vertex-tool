import unittest
from src.rlgtool import rlgtool
import filecmp
import difflib

class TestFileEqual(unittest.TestCase):
    def test_dec_command(self):
        """
        Test that the rlg file is exported correctly.
        The targeted path is expected to contain a specific rlg file, or
        else the test won't work properly
        """
        rlgtool.export_rlg_as_dae(rlgpath='./tests/files_for_testing/original/mario/mario.rlg', daepath='./tests/files_for_testing/tmp/mario.rlg.dae')
        if not filecmp.cmp('./tests/files_for_testing/tmp/mario.rlg.dae', './tests/files_for_testing/correct_dae/mario.rlg.dae'):
            wrong = open('./tests/files_for_testing/tmp/mario.rlg.dae')
            correct = open('./tests/files_for_testing/correct_dae/mario.rlg.dae')
            diff = difflib.unified_diff(correct.readlines(), wrong.readlines())
            for line in diff:
                print(line)
            self.fail('Files do not match')

    def test_patch_command(self):
        """
        Test that the rlg file is patched correctly.
        The targeted path is expected to contain a specific rlg file, or
        else the test won't work properly
        """
        rlgtool.generate_rlg_from_rlg_and_dae(srcrlgpath='./tests/files_for_testing/original/mario/mario.rlg',
                                    dstrlgpath='./tests/files_for_testing/tmp/mario.rlg',
                                    daepath='./tests/files_for_testing/correct_dae/mario.rlg.dae')
        if not filecmp.cmp('./tests/files_for_testing/correct_rlg/mario.rlg', './tests/files_for_testing/tmp/mario.rlg'):
            self.fail('Files do not match')