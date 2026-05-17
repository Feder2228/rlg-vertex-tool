from src.rlgtool.rlg_data_structures import *
import unittest


class TestRlgDataStructures(unittest.TestCase):
    def test_match_mesh_order_1(self):
        """
        Test that the hashes match
        """
        initial_order = (0x262D336F,
                         0x4c2a22a6,
                         0x4ed75f10,
                         0x651ec2fc,
                         0x90d467ea,
                         0xa7b63b80,
                         0xaadae8d9,
                         0xc4ab7153,
                         0xcfd9875a,
                         0xd1762b68,
                         0xe517f971,
                         0xe51948ed
                         )
        new_order = (0x651ec2fc,
                         0x90d467ea,
                         0xa7b63b80,
                         0x262D336F,
                         0x4c2a22a6,
                         0x4ed75f10,
                         0xaadae8d9,
                         0xc4ab7153,
                         0xcfd9875a,
                         0xd1762b68,
                         0xe51948ed,
                         0xe517f971
                         )
        main_model = RlgModel()
        other_model = RlgModel()
        for hash_id in initial_order:
            main_model.meshes.append(RlgMesh(hash_id=hash_id))
        for hash_id in new_order:
            other_model.meshes.append(RlgMesh(hash_id=hash_id))
        
        main_model.match_mesh_order(other=other_model)

        for i, main_mesh in enumerate(main_model.meshes):
            self.assertEqual(main_mesh.hash_id, new_order[i])




    def test_match_mesh_order_2(self):
        """
        Test that the hashes match
        """
        initial_order = (0x90d467ea,
                         0xc4ab7153
                         )
        new_order = (0x651ec2fc,
                         0x90d467ea,
                         0xa7b63b80,
                         0x262D336F,
                         0x4c2a22a6,
                         0x4ed75f10,
                         0xaadae8d9,
                         0xc4ab7153,
                         0xcfd9875a,
                         0xd1762b68,
                         0xe51948ed,
                         0xe517f971
                         )
        main_model = RlgModel()
        other_model = RlgModel()
        for hash_id in initial_order:
            mesh = RlgMesh(hash_id=hash_id)
            mesh.vertices.append(RlgVertex())
            mesh.faces.append(RlgFace())
            main_model.meshes.append(mesh)
        for hash_id in new_order:
            mesh = RlgMesh(hash_id=hash_id)
            mesh.vertices.append(RlgVertex())
            mesh.faces.append(RlgFace())
            other_model.meshes.append(mesh)
        
        main_model.match_mesh_order(other=other_model)

        for i, main_mesh in enumerate(main_model.meshes):
            self.assertEqual(main_mesh.hash_id, new_order[i])

        self.assertEqual(len(main_model.meshes), len(new_order))
        # check vertices
        self.assertGreater(len(main_model.meshes[1].vertices), 0)
        self.assertGreater(len(main_model.meshes[7].vertices), 0)
        for i in [0,2,3,4,5,6,8,9,10,11]:
            self.assertEqual(len(main_model.meshes[i].vertices), 0)
        # check faces
        self.assertGreater(len(main_model.meshes[1].faces), 0)
        self.assertGreater(len(main_model.meshes[7].faces), 0)
        for i in [0,2,3,4,5,6,8,9,10,11]:
            self.assertEqual(len(main_model.meshes[i].faces), 0)

        


    def test_get_list_of_mesh_hash_ids(self):
        """
        Test that the hashes match
        """
        model = RlgModel()
        correct_hash_ids = (0x262D336F,
                         0x4c2a22a6,
                         0x4ed75f10,
                         0x651ec2fc,
                         0x90d467ea,
                         0xa7b63b80,
                         0xaadae8d9,
                         0xc4ab7153,
                         0xcfd9875a,
                         0xd1762b68,
                         0xe517f971,
                         0xe51948ed
                         )
        for hash_id in correct_hash_ids:
            model.meshes.append(RlgMesh(hash_id=hash_id))
        
        hash_ids = model.get_list_of_mesh_hash_ids()

        for i in range(len(model.meshes)):
            self.assertEqual(correct_hash_ids[i], hash_ids[i])




    def test_generate_vaps(self):
        """
        Test that the V.A.P.s generate correctly
        """
        model = RlgModel()
        # mesh0
        mesh0 = RlgMesh()
        for i in range(5):
            mesh0.vertices.append(RlgVertex())
        model.meshes.append(mesh0)
        # mesh1
        mesh1 = RlgMesh()
        for i in range(5):
            mesh1.vertices.append(RlgVertex())
        model.meshes.append(mesh1)
        # mesh2
        mesh2 = RlgMesh()
        for i in range(20):
            mesh2.vertices.append(RlgVertex())
        model.meshes.append(mesh2)

        model.generate_vaps()
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.POSITION).offset, 0)
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.NORMAL).offset, 60)
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.UV0).offset, 120)
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.UNK0).offset, 140)
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.UNK1).offset, 160)
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.UNK2).offset, 180)
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.UNK3).offset, 200)
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.UNK4).offset, 220)
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.BONE_INDICES).offset, 240)
        self.assertEqual(mesh0.get_vap_by_type(type=RlgVAPType.BONE_WEIGHTS).offset, 260)
        self.assertEqual(mesh1.get_vap_by_type(type=RlgVAPType.POSITION).offset, 340)




    def test_decode_indices(self):
        """
        Test that the indices are decoded correctly
        """
        mesh = RlgMesh()
        indices = [0,1,5,5,5,0,
                    0,5,4,4,4,1,
                    1,2,6,6,6,1,
                    1,6,5,5,5,2,
                    2,3,7,7,7,2,
                    2,7,6,6,6,3,
                    3,0,4,4,4,3,
                    3,4,7,7,7,4,
                    4,5,6,6,6,4,
                    4,6,7,7,7,0,
                    0,2,1,1,1,0,
                    0,3,2
                    ]
        mesh.decode_indices(indices=indices)

        correct_face_indices = [
            [0,1,5],
            [0,5,4],
            [1,2,6],
            [1,6,5],
            [2,3,7],
            [2,7,6],
            [3,0,4],
            [3,4,7],
            [4,5,6],
            [4,6,7],
            [0,2,1],
            [0,3,2]
        ]

        self.assertEqual(len(mesh.faces), len(correct_face_indices))
        for i in range(len(mesh.faces)):
            self.assertEqual(mesh.faces[i].indices, correct_face_indices[i]),




    def test_encode_indices(self):
        """
        Test that the indices are encoded correctly
        """
        mesh = RlgMesh()
        face_indices = [
            [0,1,5],
            [0,5,4],
            [1,2,6],
            [1,6,5],
            [2,3,7],
            [2,7,6],
            [3,0,4],
            [3,4,7],
            [4,5,6],
            [4,6,7],
            [0,2,1],
            [0,3,2]
        ]
        for f in face_indices:
            mesh.faces.append(RlgFace(indices=f))

        correct_indices = [0,1,5,5,5,0,
                            0,5,4,4,4,1,
                            1,2,6,6,6,1,
                            1,6,5,5,5,2,
                            2,3,7,7,7,2,
                            2,7,6,6,6,3,
                            3,0,4,4,4,3,
                            3,4,7,7,7,4,
                            4,5,6,6,6,4,
                            4,6,7,7,7,0,
                            0,2,1,1,1,0,
                            0,3,2,2,2
                            ]
        
        indices = mesh.encode_indices()   

        self.assertEqual(len(indices), len(correct_indices))
        for i in range(len(correct_indices)):
            self.assertEqual(indices[i], correct_indices[i]),