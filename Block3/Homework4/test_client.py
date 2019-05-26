import unittest, time
from client import create_presence_meassage,start_client
from config import *

class TestCreate_Presence_Meassage(unittest.TestCase):

    def testAccountNameLen(self):
        with self.assertRaises(ValueError):
            create_presence_meassage('XXXxxxVasyaNagibat0r_3000xxxXXX')

    def testAccountNameType(self):
        with self.assertRaises(TypeError):
            create_presence_meassage(11561)

    def testDefaultUsername(self):
        self.assertEqual(create_presence_meassage()['user']['account_name'],"Guest")

class TestStartClient(unittest.TestCase):

    def testUnknownServer(self):
        with self.assertRaises(ValueError):
            start_client(156,'asa')

    def testUnknownResponseCode(self):
        PRESENCE = 'Unknown'
        with self.assertRaises(UnknownCode):
            start_client('127.0.0.1', server_port, 'Unknown')


if __name__ == "__main__":
    unittest.main()

    #Ran 10 tests in 0.014s
    #OK