# github-classifier

**short description**

This repository contains a deep-learning based classification tool for software repositories. The tool utilizes the ecore metamodel 'type graph' and a graph convolutional network. To use the tool, run 'main.py' after adding the directory containing the repositories you want to classify.

If you want to train the tool with different labels, replace the current labels with your own (or add them to the labels) in GraphClasses.py, and in function 'multi_hot_encoding' in Encoder.py. Optionally also in function 'count_class_elements' in CustomDataset.py if you want to know the number of samples in each class in your dataset. 
The labels in the tool are not mutually exclusive and are multi-hot encoded.

Currently, the tool only processes Python files.

**labels**

Application, Framework, Library, Plugin

**data**

Dataset with Python software repositories from GitHub, all with a dependency on at least one ML library.
The labeled repositories the tool is trained with are in data/labeled_dataset_repos.xlsx.

**requirements**

pyecore~=0.14.0 or higher versions

autopep8

GRaViTY tool for visualizing the metamodels, see https://github.com/GRaViTY-Tool/gravity-tool?tab=readme-ov-file for instructions on how to install the tool
