import sys
sys.path.append('../draculog/')

from Modules import Code_Initalizer

import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()