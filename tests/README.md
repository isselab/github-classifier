# github-classifier unit tests

**short description**

The unit tests test_ATE_Converter.py, test_ETM_Converter.py, and test_Custom_Dataset.py are for testing the basic functionality of the two converters and loading the dataset.
Due to the arbitrariness of real-world software repositories, the unit tests do not cover every case encountered there.
It is assumed that the unit_tests remain in this folder, otherwise the paths in the different testing functions will have to be manually adjusted, or some tests will fail.
Since Basic.ecore is not a python module, and the ATE-Converter expects the file to be in the same directory as the current file calling the converter, the Basic.ecore file is in this test folder as well.

**requirements**

pyecore~=0.14.0 or higher versions

autopep8

GRaViTY tool for visualizing the metamodels, see https://github.com/GRaViTY-Tool/gravity-tool?tab=readme-ov-file for instructions on how to install the tool
