import sys
sys.path.append('../draculog/')

import os

from Modules import Code_Initalizer

import unittest

class Installation(unittest.TestCase):
    def test_install_script(self):
        installer = Code_Initalizer.Installer(True)
        ConfigResult = os.path.isfile('ReadMe.ini')
        print("Config: " + str(ConfigResult))
        SourceResult = os.path.isdir('Source/')
        print("Source: " + str(SourceResult))
        ParamsResult = os.path.isfile('Source/params.ini')
        print("Params: " + str(ParamsResult))
        self.assertEqual(True, (ConfigResult and SourceResult and ParamsResult) )  # add assertion here

    def test_re_installation(self):
        installer = Code_Initalizer.Installer(False)
        ConfigResult = os.path.isfile('ReadMe.ini')
        print("Config: " + str(ConfigResult))
        SourceResult = os.path.isdir('Source/')
        print("Source: " + str(SourceResult))
        ParamsResult = os.path.isfile('Source/params.ini')
        print("Params: " + str(ParamsResult))
        self.assertEqual(True, ConfigResult and SourceResult and ParamsResult)  # add assertion here

    def test_compile_code(self):
        sourceDirectory = "Source/sorts"
        installer = Code_Initalizer.Installer(False, False)
        self.assertEqual(True, installer.ReCompile(sourceDirectory))

class ConfigReading(unittest.TestCase):
    def test_reading_config(self):

        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()


