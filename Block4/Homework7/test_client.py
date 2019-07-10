import unittest
from client import create_presence_meassage, start_client
from server import start_server
from config import *
from multiprocessing import Process


class TestCreate_Presence_Meassage(unittest.TestCase):

    def testAccountNameLen(self):
        with self.assertRaises(ValueError):
            create_presence_message('XXXxxxVasyaNagibat0r_3000xxxXXX', 1123)

    def testAccountNameType(self):
        with self.assertRaises(TypeError):
            create_presence_message(11561, "220")

    def testDefaultUsername(self):
        self.assertEqual(create_presence_meassage()[
                         'user']['account_name'], "Guest")


class TestStartClient(unittest.TestCase):

    def testUnknownServer(self):
        with self.assertRaises(ValueError):
            start_client(156, 'asa')

    def testConnectError(self):
        with self.assertRaises(Exception):
            start_client('132.0.0.0', 21)

    def testUnknownResponseCode(self):
        serverProcess = Process(target=start_server)
        serverProcess.start()
        with self.assertRaises(UnknownCode):
            start_client('127.0.0.1', server_port, 'Unknown')
        serverProcess.terminate()


if __name__ == "__main__":
    unittest.main()

    # Ran 10 tests in 0.014s
    # OK
