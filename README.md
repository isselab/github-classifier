# Classifier for GitHub Repos

## Table of Contents
- [Intro](#intro)
- [Installation for Users](#installation-instruction-for-users)
- [Installation for Devs](#installation-instruction-for-devs)
- [Expectation for Devs](#expectation-for-devs)
- [Known Problems / Limitations](#known-problems--limitations)
- [Help](#help)

## Intro:

This repository features a deep learning classifier designed for the analysis of software repositories.
The tool employs the ecore metamodel's 'type graph' in conjunction with a graph convolutional network.
Presently, the classifier categorizes repositories into four distinct classes: Application, Framework, Library, and Plugin.
It is important to note that the labels utilized by the tool are **not mutually exclusive** and are represented in a multi-hot encoded format.

## Installation Instruction for Users:
1. Clone the repository by executing the following command:  
`git clone https://github.com/isselab/github-classifier.git`
2. Open the cloned repository using your preferred Integrated Development Environment (IDE).  
For the purposes of this instruction, we will assume the use of PyCharm from JetBrains.
3. Change the directory to data/input by running the following command:  
`cd ~/data/input`
4. Clone the repositories you wish to analyze by executing:  
`git clone LINK_TO_REPO_YOU_WANT`
5. run main.py

The default threshold for identification is set at 50%.
If you wish to modify this threshold, please locate the relevant settings in the settings.py file.
After making the necessary adjustments, ensure to rerun main.py to apply the changes.

## Installation Instruction for Devs:

### Basic Installation:
1. Clone the repository by executing the following command:  
`git clone https://github.com/isselab/github-classifier.git`
2. Open the cloned repository using your preferred Integrated Development Environment (IDE).

### Retraining:
1. Check data/labeled_dataset_repos.xlsx.  
This xlsx file contains the labeled repository's the tool is trained with.  
You may want to change it accordingly to your needs.
2. We strongly recommend utilizing a GPU for training purposes.  
To verify GPU availability, please run the TorchGPUCheck.py script.  
If you get the Result "Cuda is available!" you may proceed to step 3.  
If the output indicates that "Cuda is not available," please follow the instructions provided in the terminal.      
Additionally, refer to the guide in the [Help](#help) section for further assistance in resolving any issues.
3. Run prepareDataset.py
4. Change the experiment_name in settings.py in the training section.
5. Run training.py


## Expectation for Devs:
### Recommended Workflow:
1. Create an issue in the GitHub issue page.
2. Open a branch named after the issue
3. Write code that fixes the issue
4. Write test code to be sure it works.
5.  Comment your code well to be sure it can be understood.
6. Create a merge request

## Known Problems / Limitations:
- The Tool only processes Python files.
- Dataset contains Python software repositories from GitHub, all with a dependency on at least one ML library.
- Labels can not be changed easily, WIP

## Help
- Torch CUDA Guide, see "https://www.geeksforgeeks.org/how-to-set-up-and-run-cuda-operations-in-pytorch/"
- GRaViTY tool for visualizing the metamodels, see "https://github.com/GRaViTY-Tool/gravity-tool?tab=readme-ov-file"
