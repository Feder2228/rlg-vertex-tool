import unittest
from src.rlgtool import shier
from src.rlgtool import rlg
from src.rlgtool import nlgutil
from src.rlgtool import util
from src.rlgtool import rlg_data_structures


class TestShier(unittest.TestCase):
    def test_get_parent_bone_hash(self):
        """
        Test the method
        """
        shierfile = open('./tests/test_files/mario.shier', 'rb')
        parent_bone_hash = shier.get_parent_bone_hash(shierfile=shierfile, bone_hash=0x4EEE263C)
        self.assertEqual(parent_bone_hash, 0xE3C524D)

    def test_organize_bone_hierarchy(self):
        """
        Test the methods
        """
        shierfile = open('./tests/test_files/mario.shier', 'rb')
        rlgfile = open('./tests/test_files/mario.rlg', 'rb')
        rlg_section_map = nlgutil.get_map_of_sections(rlgfile)
        model = rlg_data_structures.RlgModel(hash_id=0xBBFFCF5E, mesh_count=12, unk0x8=0x12F8F4)
        rlg.add_bones_to_model(rlgfile=rlgfile, section=rlg_section_map[rlg.SECTION_BONE_MATRICES][0], model=model)
        shier.organize_bone_hierarchy(shierfile=shierfile, model=model)
        # test the data
        binfile = open('./tests/test_files/hashid.bin', 'rb')
        print(bone_tree(model.root_bone, binfile=binfile))
        self.assertEqual(model.root_bone.children[0].hash_id, 0xA149C14E)
        self.assertEqual(model.root_bone.children[1].hash_id, 0xD693D55A)
    

def bone_tree(root : rlg_data_structures.RlgBone, level=0, binfile=None) -> str:
    INDENT = '.   '
    s = ''
    if binfile == None: 
        s += hex(root.hash_id)
    else:
        try:
            s += nlgutil.get_hash_name(binfile=binfile, hash=root.hash_id).replace(' ', '_')
        except:
            s += 'root'
    s += '\n'
    for bone in root.children:
        s += (INDENT * level)
        s += bone_tree(root=bone, level=level+1, binfile=binfile)
    return s
        
        
