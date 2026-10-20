from src.rlgtool.rlg_data_structures import *
import unittest


class TestRlgDataStructures(unittest.TestCase):
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




    def test_encode_indices_naive(self):
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
            self.assertEqual(indices[i], correct_indices[i])



    def test_encode_indices_1(self):
        mesh = RlgMesh()
        face_indices = [
            [0,1,2],
            [0,5,4],
            [1,2,6],
            [3,4,5],
            [4,5,7],
            [5,6,8],
            [8,10,6]
        ]
        for f in face_indices:
            mesh.faces.append(RlgFace(indices=f))

        correct_indices = [
            1,2,0,0,
            0,5,4,4,
            4,1,1,2,
            6,6,6,5,
            5,3,4,4,
            4,5,7,7,
            7,8,8,5,
            6,6,6,8,
            10,10,10
                            ]
        
        indices = mesh.encode_indices()   

        print(indices)
        self.assertEqual(len(indices), len(correct_indices))
        for i in range(len(correct_indices)):
            self.assertEqual(indices[i], correct_indices[i])