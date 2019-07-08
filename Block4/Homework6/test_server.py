import unittest
from server import check_correct_presence_and_response, start_server
from config import *


class TestCheckMessages(unittest.TestCase):

    def testTimeIsFloat(self):
        self.assertEqual(
            check_correct_presence_and_response(
                {
                    'action': 'presence', 'time': 15589028, 'user': {
                        'account_name': 'SuperUser'}}), {
                    'response': 400, 'error': 'Не верный запрос'})

    def testCorrectMessage(self):
        self.assertEqual(
            check_correct_presence_and_response(
                {
                    'action': 'presence', 'time': 1558902800.913287, 'user': {
                        'account_name': 'SuperUser'}}), {
                    'response': 200})

    def testHaveAction(self):
        self.assertEqual(check_correct_presence_and_response({'time': 1558902800.913287, 'user': {
                         'account_name': 'SuperUser'}}), {'response': 400, 'error': 'Не верный запрос'})

    def testAccountIsPresence(self):
        self.assertEqual(
            check_correct_presence_and_response(
                {
                    'action': 'goodbye', 'time': 1558902800.913287, 'user': {
                        'account_name': 'SuperUser'}}), {
                    'response': 400, 'error': 'Не верный запрос'})

    def testShutdownCommand(self):
        self.assertEqual(
            check_correct_presence_and_response(
                {
                    'action': 'Stop server', 'time': 1558902800.913287, 'user': {
                        'account_name': 'Admin'}}), {
                    'response': 0})
        # self.assertEqual(start_server()["alive"],False)


class TestStartServer(unittest.TestCase):

    def testUnknownServerReq(self):
        with self.assertRaises(ValueError):
            start_server(156, 'asa')


if __name__ == "__main__":
    unittest.main()

    # Ran 10 tests in 0.014s
    # OK
