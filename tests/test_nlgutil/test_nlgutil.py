from src.rlgtool import nlgutil
import filecmp
import unittest
from src.rlgtool import rlg


class TestNlgutil(unittest.TestCase):
    def test_get_section_tree(self):
        rlgfile = open('./tests/files_for_testing/original/mario/mario.rlg', 'rb')
        l1 = nlgutil.get_section_tree(rlgfile)
        self.assertEqual(len(l1), 1)
        print(section_tree(l1[0]))
        self.assertEqual(len(l1[0].get_children_of_type(rlg.SECTION_MESH_DATA)), 1)


    def test_copy_section(self):
        """
        Test the method add_models_to_root
        """
        srcrlg = open('./tests/test_files/mario.rlg', 'rb')
        dstrlg = open('./tests/test_files/mario_copy.rlg', 'wb')
        root = nlgutil.get_section_tree(srcrlg)

        nlgutil.write_section_header(rlgfile=dstrlg, section=root)
        for section in root.children:
            if section.type not in (rlg.SECTION_CONTAINER, rlg.SECTION_BONE_MATRICES, rlg.SECTION_BONE_MESH_HASHES, rlg.SECTION_BONE_UNKNOWN):
                nlgutil.copy_section(src=srcrlg, dst=dstrlg, section=section)
        
        if not filecmp.cmp('./tests/test_files/mario.rlg', './tests/test_files/mario_copy.rlg'):
            self.fail('Files do not match')



def section_tree(root : nlgutil.Section, level=0) -> str:
    INDENT = '.   '
    s = ''
    s += hex(int.from_bytes(root.type))
    s += '\n'
    for section in root.children:
        s += (INDENT * level)
        s += section_tree(root=section, level=level+1)
    return s