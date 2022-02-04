import sys

sys.path.append('../draculog/')

import os

from Modules import Code_Initalizer

import unittest


class Installation(unittest.TestCase):

    @unittest.skip("Skipping Installation test as we know it works")
    def test_install_script(self):
        print("Testing Fresh Install")
        installer = Code_Initalizer.Installer(True)
        ConfigResult = os.path.isfile('ReadMe.ini')
        print("Config: " + str(ConfigResult))
        SourceResult = os.path.isdir('Source/')
        print("Source: " + str(SourceResult))
        ParamsResult = os.path.isfile('Source/params.ini')
        print("Params: " + str(ParamsResult))
        self.assertEqual(True, (ConfigResult and SourceResult and ParamsResult))  # add assertion here

    @unittest.skip("Skipping Re-Installation test as we know it works")
    def test_re_installation(self):
        print("Testing Reinstall")
        installer = Code_Initalizer.Installer(False)
        ConfigResult = os.path.isfile('ReadMe.ini')
        print("Config: " + str(ConfigResult))
        SourceResult = os.path.isdir('Source/')
        print("Source: " + str(SourceResult))
        ParamsResult = os.path.isfile('Source/params.ini')
        print("Params: " + str(ParamsResult))
        self.assertEqual(True, ConfigResult and SourceResult and ParamsResult)  # add assertion here

    compiler = Code_Initalizer.CodeCompiler()

    def test_compile_code(self):
        print("Testing Compilation of Code 1")
        sourceDirectory = "Source/sorts"
        compiler = Code_Initalizer.CodeCompiler()
        self.assertEqual(True, compiler.Compile_Code(sourceDirectory))

    def test_compile_code(self):
        print("Testing Compilation of Code 2")
        sourceDirectory = "Source/sorts"
        compiler2 = Code_Initalizer.CodeCompiler()
        self.assertEqual("sort-clang", compiler2.FindCompiledCode(self, sourceDirectory))


class ConfigReading(unittest.TestCase):
    @unittest.skip("Skipping Reading Config Test as it's not ready yet")
    def test_reading_config(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
