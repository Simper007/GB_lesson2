import unittest
from server import Server
from config import *


class TestCheckMessages(unittest.TestCase):
    """
    Тесты unitest для серверного кода
    """

    def testTimeIsFloat(self):
        self.assertEqual(
            Server.check_correct_presence_and_response(
                self, {
                    'action': 'presence', 'time': 15589028, 'user': {
                        'account_name': 'SuperUser'}}), {
                'response': 400, 'error': 'Не верный запрос'})

    def testCorrectMessage(self):
        self.assertEqual(
            Server.check_correct_presence_and_response(
                self, {
                    'action': 'presence', 'time': 1558902800.913287, 'user': {
                        'account_name': 'SuperUser'}}), {
                'response': 200})

    def testHaveAction(self):
        self.assertEqual(
            Server.check_correct_presence_and_response(
                {
                    'time': 1558902800.913287, 'user': {
                        'account_name': 'SuperUser'}}), {
                    'response': 400, 'error': 'Не верный запрос'})

    def testAccountIsPresence(self):
        self.assertEqual(
            Server.check_correct_presence_and_response(
                self, {
                    'action': 'goodbye', 'time': 1558902800.913287, 'user': {
                        'account_name': 'SuperUser'}}), {
                'response': 400, 'error': 'Не верный запрос'})

    def testShutdownCommand(self):
        self.assertEqual(
            Server.check_correct_presence_and_response(
                self, {
                    'action': 'Stop server', 'time': 1558902800.913287, 'user': {
                        'account_name': 'Admin'}}), {
                'response': 0})
        # self.assertEqual(start_server()["alive"],False)


class TestStartServer(unittest.TestCase):

    def testUnknownServerReq(self):
        with self.assertRaises(ValueError):
            Server.start_server(self)


if __name__ == "__main__":
    unittest.main()

    # Ran 10 tests in 0.014s
    # OK
