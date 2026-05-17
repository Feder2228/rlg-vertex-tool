from src.rlgtool import dae
import unittest


class TestStrToNumList(unittest.TestCase):
    def test_1(self):
        """
        Test that the method works
        """
        string = '1 2 3.2 4 5'
        output = dae.str_to_num_list(string=string)
        self.assertEqual(output, [1, 2, 3.2, 4, 5])

    
    def test_2(self):
        """
        Test that the stride argument works as intended
        """
        string = '1 2 3 4 5 6'
        output = dae.str_to_num_list(string=string, group=2)
        self.assertEqual(output, [[1, 2], [3, 4], [5, 6]])


    def test_3(self):
        """
        Test the input count and the offset parameters
        """
        string = '0 1 2 3 4 5'
        output = dae.str_to_num_list(string=string, step=3, offset=0)
        self.assertEqual(output, [0, 3])


    def test_4(self):
        """
        Test the input count and the offset parameters
        """
        string = '0 1 2 3 4 5'
        output = dae.str_to_num_list(string=string, step=3, offset=2)
        self.assertEqual(output, [2, 5])


    def test_5(self):
        """
        Test the input count and the offset parameters, in combination with stride
        """
        string = '0 10 20 30 40 51 61 71 81 91 102 112 122 132 142 153 163 173 183 193'
        output = dae.str_to_num_list(string=string, group=2, step=5, offset=2)
        self.assertEqual(output, [[20, 71], [122, 173]])