import unittest
import CustomAPI


class TestCustomAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = CustomAPI.Backend()
        cls.count = 10
        cls.name = "testuser"
        cls.password = "testpw"
        cls.uid = None

    def test_00_create_user(self):
        self.assertTrue(self.session.create_user(self.name, self.password))

    def test_01_login(self):
        self.assertTrue(self.session.login(self.name, self.password))
        self.uid = self.session.get_user_id(self.name, self.password)

    def test_02_create_api(self):
        for i in range(1, self.count):
            name = "test{}".format(i)
            data = "test{}data".format(i)
            channel = "test{}channel".format(i)
            self.assertTrue(self.session.create_api(name, data, channel))

    def test_03_edit_api(self):
        for i in range(1, self.count):
            name = "edit{}".format(i)
            data = "edit{}data".format(i)
            channel = "edit{}channel".format(i)
            self.assertTrue(self.session.edit_api(i, name, data, channel))

    def test_04_fetch_api_data(self):
        for i in range(1, self.count):
            data = "edit{}data".format(i)
            channel = "edit{}channel".format(i)
            fetched_data = self.session.fetch_api_data(i, channel)
            self.assertEqual(fetched_data, data)

    def test_05_delete_api(self):
        for i in range(1, self.count):
            self.assertTrue(self.session.delete_api(i))

    def test_06_delete_user(self):
        uid = self.session.get_user_id(self.name, self.password)
        self.assertTrue(self.session.delete_user(uid))

    def test_07_logout(self):
        self.assertTrue(self.session.logout())
