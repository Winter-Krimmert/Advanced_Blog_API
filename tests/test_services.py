import unittest

class SimpleTest(unittest.TestCase):
    def test_pass(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
