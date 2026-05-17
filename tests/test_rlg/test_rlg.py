import unittest
from src.rlgtool import rlg
from src.rlgtool import nlgutil
from src.rlgtool import util
from src.rlgtool import rlg_data_structures


class TestRlg(unittest.TestCase):
    def test_add_models_to_root(self):
        """
        Test the method add_models_to_root
        """
        # correct data
        # BB FF CF 5E 00 00 00 0C 00 12 F8 F4
        correct_model = rlg_data_structures.RlgModel(hash_id=0xBBFFCF5E, mesh_count=12, unk0x8=0x12F8F4)
        # data to be tested
        root = rlg_data_structures.RlgRoot([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]])
        rlgfile = open('./tests/test_files/mario.rlg', 'rb')
        section_map = nlgutil.get_map_of_sections(rlgfile)
        rlg.add_models_to_root(rlgfile, section_map[rlg.SECTION_MODEL_DATA][0], root)
        model = root.models[0]
        # run the test
        self.assertEqual(model.hash_id, correct_model.hash_id)
        self.assertEqual(model.mesh_count, correct_model.mesh_count)
        self.assertEqual(model.unk0x8, correct_model.unk0x8)


    def test_add_meshes_to_model_mesh1(self):
        """
        Test the method add_meshes_to_model, for mesh 1
        """
        # correct data 
        correct_mesh1 = rlg_data_structures.RlgMesh(
            index_offset        = 0x2C2,
            index_format        = 0,
            index_count         = 0x24D,
            vertex_count        = 0x136,
            unk0xA              = 0x1,
            vap_count           = 0xA,
            vap_offset          = 0x50,
            material_hash_id    = 0x1ACE1D01,
            hash_id             = 0x4C2A22A6,
            unk0x18             = 0,
            unk0x1C             = 0x000D0007,
            material_offset     = 0x68,
            unk0x24             = 0,
            unk0x28             = 0,
            unk0x2C             = 0)
        # 00 00 02 C2  00 00 02 4D  01 36 01 0A  00 00 00 50
        # 1A CE 1D 01  4C 2A 22 A6  00 00 00 00  00 0D 00 07 
        # 00 00 00 68  00 00 00 00  00 00 00 00  00 00 00 00

        # Prepare the data for the test
        model = rlg_data_structures.RlgModel(hash_id=0xBBFFCF5E, mesh_count=12, unk0x8=0x12F8F4)
        # open the file
        rlgfile = open('./tests/test_files/mario.rlg', 'rb')
        section_map = nlgutil.get_map_of_sections(rlgfile)
        rlg.add_meshes_to_model(rlgfile, section_map[rlg.SECTION_MESH_DATA][0], model)
        mesh1 = model.meshes[1]
        # test
        self.assertEqual(mesh1.index_offset, correct_mesh1.index_offset)
        self.assertEqual(mesh1.index_format, correct_mesh1.index_format)
        self.assertEqual(mesh1.index_count, correct_mesh1.index_count)
        self.assertEqual(mesh1.vertex_count, correct_mesh1.vertex_count)
        self.assertEqual(mesh1.vap_count, correct_mesh1.vap_count)
        self.assertEqual(mesh1.vap_offset, correct_mesh1.vap_offset)
        self.assertEqual(mesh1.material_hash_id, correct_mesh1.material_hash_id)
        self.assertEqual(mesh1.hash_id, correct_mesh1.hash_id)
        self.assertEqual(mesh1.material_offset, correct_mesh1.material_offset)


    def test_add_vaps_to_mesh_mesh0(self):
        """
        Test the method add_vaps_to_mesh
        """
        rlgfile = open('./tests/test_files/mario.rlg', 'rb')
        section_map = nlgutil.get_map_of_sections(rlgfile)
        # first mesh. Only vap_offset and vap_count should matter really
        mesh = rlg_data_structures.RlgMesh(vap_count = 10, vap_offset = 0)
        rlg.add_vaps_to_mesh(rlgfile, section_map[rlg.SECTION_VERTEX_ATTRIBUTES][0], mesh)
        correct_vaps = [
            rlg_data_structures.RlgVertexAttributePointer(offset=0, type=rlg_data_structures.RlgVAPType.POSITION, stride=12),
            rlg_data_structures.RlgVertexAttributePointer(offset=0xA2C, type=rlg_data_structures.RlgVAPType.NORMAL, stride=12),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x1458, type=rlg_data_structures.RlgVAPType.UV0, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x17BC, type=rlg_data_structures.RlgVAPType.UNK0, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x1B20, type=rlg_data_structures.RlgVAPType.UNK1, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x1E84, type=rlg_data_structures.RlgVAPType.UNK2, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x21E8, type=rlg_data_structures.RlgVAPType.UNK3, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x254C, type=rlg_data_structures.RlgVAPType.UNK4, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x28B0, type=rlg_data_structures.RlgVAPType.BONE_INDICES, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x2C14, type=rlg_data_structures.RlgVAPType.BONE_WEIGHTS, stride=16)]
        # test
        for correct_vap in correct_vaps:
            vap = mesh.get_vap_by_type(correct_vap.type)
            self.assertEqual(vap.offset, correct_vap.offset)
            self.assertEqual(vap.stride, correct_vap.stride)


    def test_add_vertices_to_mesh_mesh0(self):
        """
        Test the method add_vertices_to_mesh
        """
        vaps = [
            rlg_data_structures.RlgVertexAttributePointer(offset=0, type=rlg_data_structures.RlgVAPType.POSITION, stride=12),
            rlg_data_structures.RlgVertexAttributePointer(offset=0xA2C, type=rlg_data_structures.RlgVAPType.NORMAL, stride=12),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x1456, type=rlg_data_structures.RlgVAPType.UV0, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x17BC, type=rlg_data_structures.RlgVAPType.UNK0, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x1B20, type=rlg_data_structures.RlgVAPType.UNK1, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x1E84, type=rlg_data_structures.RlgVAPType.UNK2, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x21E8, type=rlg_data_structures.RlgVAPType.UNK3, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x254C, type=rlg_data_structures.RlgVAPType.UNK4, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x28B0, type=rlg_data_structures.RlgVAPType.BONE_INDICES, stride=4),
            rlg_data_structures.RlgVertexAttributePointer(offset=0x2C14, type=rlg_data_structures.RlgVAPType.BONE_WEIGHTS, stride=16)]
        mesh = rlg_data_structures.RlgMesh(vaps=vaps)
        mesh.vertex_count = 0xD9
        # open the file
        rlgfile = open('./tests/test_files/mario.rlg', 'rb')
        section_map = nlgutil.get_map_of_sections(rlgfile)
        rlg.add_vertices_to_mesh(rlgfile, section_map[rlg.SECTION_VERTEX_DATA][0], mesh)
        # test
        self.assertEqual(mesh.vertices[0].position[0], util.bytes_to_float(b'\xBD\x0B\x47\x9C'))


    def test_add_bones_to_mesh(self):
        """
        Test
        """
        # A1 0E 2F 63 A1 10 10 85  C4 0B 86 C1 A1 17 BC 45
        correct_bone_hashes_0 = [0xA10E2F63, 0xA1101085, 0xC40B86C1, 0xA117BC45]
        # 93 11 F9 C2 07 1D E7 B2  EA DA DE 66 EA DA DE 65  07 1D E7 B4 EA DA DE 45  EA DA DE 44 07 1D E7 B3  EA DA DE 24
        correct_bone_hashes_1 = [0x9311F9C2, 0x071DE7B2, 0xEADADE66, 0xEADADE65, 0x071DE7B4, 0xEADADE45, 0xEADADE44, 0x071DE7B3, 0xEADADE24]
        rlgfile = open('./tests/test_files/mario.rlg', 'rb')
        section_map = nlgutil.get_map_of_sections(rlgfile)
        model = rlg_data_structures.RlgModel(hash_id=0xBBFFCF5E, mesh_count=12, unk0x8=0x12F8F4) 
        mesh_0 = rlg_data_structures.RlgMesh()
        mesh_1 = rlg_data_structures.RlgMesh()
        model.meshes.append(mesh_0)
        model.meshes.append(mesh_1)
        rlg.add_bones_to_model(rlgfile, section_map[rlg.SECTION_BONE_MATRICES][0], model)
        rlg.add_bones_to_mesh(rlgfile, section_map[rlg.SECTION_BONE_MESH_HASHES][0], model=model, mesh=mesh_0)
        rlg.add_bones_to_mesh(rlgfile, section_map[rlg.SECTION_BONE_MESH_HASHES][1], model=model, mesh=mesh_1)
        for i, bone in enumerate(mesh_0.bones):
            self.assertEqual(bone.hash_id, correct_bone_hashes_0[i])
        for i, bone in enumerate(mesh_1.bones):
            self.assertEqual(bone.hash_id, correct_bone_hashes_1[i])
        # BB 92 F1 9A 3D 90 0C AC BF 7F 5D 08  (first three floats of the first bone's matrix)
        self.assertEqual(mesh_0.bones[0].matrix[0][0], util.bytes_to_float(b'\xBB\x92\xF1\x9A'))
        self.assertEqual(mesh_0.bones[0].matrix[0][1], util.bytes_to_float(b'\x3D\x90\x0C\xAC'))
        self.assertEqual(mesh_0.bones[0].matrix[0][2], util.bytes_to_float(b'\xBF\x7F\x5D\x08'))
        self.assertEqual(mesh_0.bones[0].matrix[3][3], 1.0)
        self.assertEqual(mesh_1.bones[1].matrix[1][1], util.bytes_to_float(b'\x3F\x52\x82\x31'))
        self.assertEqual(mesh_1.bones[1].matrix[3][3], 1.0) 