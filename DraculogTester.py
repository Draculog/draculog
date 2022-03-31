import os.path
import unittest
import Draculog_Downloader as dL
import Draculog_Executor as eX
import Draculog_Uploader as uP

class DownloadTester(unittest.TestCase):
    def test_API_call(self):
        jsonObject = dL.Call_GreenCode_API("notCompiled")
        self.assertIsNotNone(jsonObject)

    def test_Make_Makefile(self):
        self.assertEqual(True, dL.Create_Makefile("", "code.cpp"))

    def test_Make_UserCode(self):
        codeString = "there is code in here"
        codePath = ""
        result1 = True if dL.Create_User_Code(codePath, "code1.cpp", codeString, True) else False
        codeString = None
        result2 = True if dL.Create_User_Code(codePath, "code2.cpp", codeString) else False
        self.assertEqual(True, result1 and result2)

    def test_Setup_UnCompiledCode(self):
        self.assertEqual(True, True)  # add assertion here

class ExecutorTester(unittest.TestCase):
    def test_API_call(self):
        self.assertEqual(True, True)  # add assertion here

    def test_Make_Makefile(self):
        self.assertEqual(True, True)  # add assertion here

    def test_Make_UserCode(self):
        self.assertEqual(True, True)  # add assertion here

    def test_Setup_UnCompiledCode(self):
        self.assertEqual(True, True)  # add assertion here

class UploadTester(unittest.TestCase):
    def test_API_call(self):
        self.assertEqual(True, True)  # add assertion here

    def test_Make_Makefile(self):
        self.assertEqual(True, True)  # add assertion here

    def test_Make_UserCode(self):
        self.assertEqual(True, True)  # add assertion here

    def test_Setup_UnCompiledCode(self):
        self.assertEqual(True, True)  # add assertion here

if __name__ == '__main__':
    unittest.main()
