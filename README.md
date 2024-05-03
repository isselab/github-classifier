# github-classifier

**short description**

This repository contains a deep-learning based classification tool for Software Repositories. The tool utilizes ecore metamodels and a graph convolutional network. For use run 'main.py' after adding the directory containing the repositories you want to classify.

If you want to train the tool with different labels, you can use GraphLabels.py to encode your labeled repositories for your dataset.

**labels**

Framework, Library, Application, Tutorial, Experiment

**data**

Contains labeled repositories from 2023-aisystemsmining

**requirements**

pyecore~=0.14.0 or higher versions

GRaViTY tool for visualizing the metamodels, see https://github.com/GRaViTY-Tool/gravity-tool?tab=readme-ov-file for instructions on how to install the tool
