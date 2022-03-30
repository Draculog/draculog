import unittest
import DraculogDownloader as dl

class DownloadTester(unittest.TestCase):
    def test_API_call(self):
        jsonObject = dl.Call_GreenCode_API("notCompiled")
        self.assertNotEqual(None, jsonObject)  # add assertion here

    def test_Parsed_Response(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
