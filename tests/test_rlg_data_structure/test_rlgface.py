from src.rlgtool.rlg_data_structures import *
import unittest


class TestRlgDataStructures(unittest.TestCase):
    def test_shift_index_to_end(self):
        face = RlgFace([0,1,2])
        face.shift_index_to_end(1)
        self.assertEqual(face.indices, [2,0,1])
        face.shift_index_to_end(0)
        self.assertEqual(face.indices, [1,2,0])


    def test_shift_index_to_start(self):
        face = RlgFace([0,1,2])
        face.shift_index_to_start(2)
        self.assertEqual(face.indices, [2,0,1])
        face.shift_index_to_start(2)
        self.assertNotEqual(face.indices, [0,1,2])
        face.shift_index_to_start(1)
        self.assertEqual(face.indices, [1,2,0])
        face.shift_index_to_start(0)
        self.assertEqual(face.indices, [0,1,2])


    def test_shift_sequence_to_end(self):
        face = RlgFace([0,1,2])
        face.shift_sequence_to_end([0,1])
        self.assertEqual(face.indices, [2,0,1])
        face.shift_sequence_to_end([1,2])
        self.assertEqual(face.indices, [0,1,2])
        face.shift_sequence_to_end([2,0])
        self.assertEqual(face.indices, [1,2,0])
        with self.assertRaises(Exception):
            face.shift_sequence_to_end([1,0])
        with self.assertRaises(Exception):
            face.shift_sequence_to_end([2,1])
        with self.assertRaises(Exception):
            face.shift_sequence_to_end([0,2])


    def test_shift_sequence_to_start(self):
        face = RlgFace([0,1,2])
        face.shift_sequence_to_start([0,1])
        self.assertEqual(face.indices, [0,1,2])
        face.shift_sequence_to_start([1,2])
        self.assertEqual(face.indices, [1,2,0])
        face.shift_sequence_to_start([2,0])
        self.assertEqual(face.indices, [2,0,1])
        with self.assertRaises(Exception):
            face.shift_sequence_to_start([1,0])
        with self.assertRaises(Exception):
            face.shift_sequence_to_start([2,1])
        with self.assertRaises(Exception):
            face.shift_sequence_to_start([0,2])


    def test_get_shared_indices(self):
        face1 = RlgFace([0,1,2])
        self.assertEqual(face1.get_shared_indices(RlgFace([0,1,2])), [0,1,2])
        self.assertEqual(face1.get_shared_indices(RlgFace([2,3,4])), [2])
        self.assertEqual(face1.get_shared_indices(RlgFace([1,2,4])), [1,2])
        self.assertEqual(face1.get_shared_indices(RlgFace([4,1,2])), [1,2])
        self.assertEqual(face1.get_shared_indices(RlgFace([2,4,1])), [1,2])
        self.assertEqual(face1.get_shared_indices(RlgFace([0,2,4])), [2,0])
        self.assertEqual(face1.get_shared_indices(RlgFace([4,0,2])), [2,0])
        self.assertEqual(face1.get_shared_indices(RlgFace([2,4,0])), [2,0])


    def test_flip(self):
        face1 = RlgFace([0,1,2])
        face1.flip()
        self.assertEqual(face1.indices, [1,0,2])


    def test_determine_relationship(self):
        face1 = RlgFace([0,1,2])
        self.assertEqual(face1.determine_relationship(RlgFace([3,4,5]), is_self_locked=False), 0)
        # Not locked, case 1
        self.assertEqual(face1.determine_relationship(RlgFace([0,4,5]), is_self_locked=False), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,0,5]), is_self_locked=False), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,4,0]), is_self_locked=False), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([1,4,5]), is_self_locked=False), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,1,5]), is_self_locked=False), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,4,1]), is_self_locked=False), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([2,4,5]), is_self_locked=False), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,2,5]), is_self_locked=False), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,4,2]), is_self_locked=False), 1)
        # Locked, case 1
        self.assertEqual(face1.determine_relationship(RlgFace([0,4,5]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([3,0,5]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([3,4,0]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([1,4,5]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([3,1,5]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([3,4,1]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([2,4,5]), is_self_locked=True), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,2,5]), is_self_locked=True), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,4,2]), is_self_locked=True), 1)
        # Not locked, case 2
        self.assertEqual(face1.determine_relationship(RlgFace([0,1,5]), is_self_locked=False), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([3,0,1]), is_self_locked=False), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([1,4,0]), is_self_locked=False), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([1,2,5]), is_self_locked=False), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([3,1,2]), is_self_locked=False), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([2,4,1]), is_self_locked=False), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([2,0,5]), is_self_locked=False), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([3,2,0]), is_self_locked=False), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([0,4,2]), is_self_locked=False), 2)
        # Locked, case 2
        self.assertEqual(face1.determine_relationship(RlgFace([0,1,5]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([3,0,1]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([1,4,0]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([1,2,5]), is_self_locked=True), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([3,1,2]), is_self_locked=True), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([2,4,1]), is_self_locked=True), 2)
        self.assertEqual(face1.determine_relationship(RlgFace([2,0,5]), is_self_locked=True), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,2,0]), is_self_locked=True), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([0,4,2]), is_self_locked=True), 1)
        # Not locked, case 3
        self.assertEqual(face1.determine_relationship(RlgFace([1,0,5]), is_self_locked=False), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([3,1,0]), is_self_locked=False), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([0,4,1]), is_self_locked=False), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([2,1,5]), is_self_locked=False), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([3,2,1]), is_self_locked=False), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([1,4,2]), is_self_locked=False), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([0,2,5]), is_self_locked=False), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([3,0,2]), is_self_locked=False), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([2,4,0]), is_self_locked=False), 3)
        # Locked, case 3
        self.assertEqual(face1.determine_relationship(RlgFace([1,0,5]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([3,1,0]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([0,4,1]), is_self_locked=True), 0)
        self.assertEqual(face1.determine_relationship(RlgFace([2,1,5]), is_self_locked=True), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([3,2,1]), is_self_locked=True), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([1,4,2]), is_self_locked=True), 3)
        self.assertEqual(face1.determine_relationship(RlgFace([0,2,5]), is_self_locked=True), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([3,0,2]), is_self_locked=True), 1)
        self.assertEqual(face1.determine_relationship(RlgFace([2,4,0]), is_self_locked=True), 1)

    def test_contains_sequence(self):
        face1 = RlgFace([0,1,2])
        self.assertTrue(face1.contains_sequence([0,1]))
        self.assertTrue(face1.contains_sequence([1,2]))
        self.assertTrue(face1.contains_sequence([2,0]))
        self.assertFalse(face1.contains_sequence([1,0]))
        self.assertFalse(face1.contains_sequence([2,1]))
        self.assertFalse(face1.contains_sequence([0,2]))
        self.assertFalse(face1.contains_sequence([0,3]))


    