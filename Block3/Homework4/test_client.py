import unittest, time
from .client import create_presence_meassage,start_client

class TestCreate_Presence_Meassage(unittest.TestCase):
    def testAccount_name_len(self):
        with self.assertRaises(TypeError):
            create_presence_meassage('XXXxxxVasyaNagibat0r_3000xxxXXX')


if __name__ == "__main__":
    unittest.main()