import unittest

from model.substitution import Substitution


class SubstitutionTestCase(unittest.TestCase):
    """Test cases for class `Substitution`."""

    def test_init(self):
        Substitution('a', "function(a,r1,[b,c])")
        Substitution('a', "function( a , r1 , [b,c])")
        Substitution('a', "function( a , r1 , [ b , c ] )")
        with self.assertRaises(Exception):
            Substitution('a', "function(a, r1, invalid)")
        with self.assertRaises(Exception):
            Substitution('a', "function(a, r1, [b, c], invalid)")


if __name__ == '__main__':
        unittest.main()
