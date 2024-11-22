"""
Settings Configuration for the github-classifier

This module contains configuration settings for the training process and 
dataset preparation for the model. It includes paths, hyperparameters, 
and other relevant settings.
"""

import os

# Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Training Configuration
TRAINING_SETTINGS = {
    'output_directory': os.path.join('data/output'), # Path to the folder containing the converted repositories
    'labels_file': os.path.join(BASE_DIR, 'data/labeled_dataset_repos.xlsx'), # Path to the Excel file containing labeled dataset information
    'n_epoch': 100, # Number of epochs for training the model
    'k_folds': 4,  # Number of folds for k-fold cross-validation; set to 1 to disable, must be at least 2 to be active
    'learning_rate': 0.001,# Learning rate for the optimizer; controls the step size during gradient descent
    'figure_output': os.path.join('data/output/training_test_plot'), # Path to save plots generated during training/testing
    'threshold': 0.5,  # Value above which label is considered predicted by model in training
    'save_classification_reports': os.path.join(BASE_DIR, 'classification_reports/train.txt'), # Path to save classification reports after training
    'experiment_name': 'train', # Name of the experiment; is used for logging and tracking purposes
}

# Dataset Preparation Configuration
DATASET_PREPARATION_SETTINGS = {
    'repository_directory': os.path.join('data/input'),  # Path to GitHub repositories used as input
    'output_directory': os.path.join('data/output'), # Path to the folder containing the converted repositories
    'repository_list_file': os.path.join(BASE_DIR, 'data/labeled_dataset_repos.xlsx'), # Path to the Excel file containing labeled dataset information
    'download_from_repository_list' : False # Boolean flag; True -> Download all repos from repository_list_files; False -> Do not download from repository_list
}

# Main Configuration
MAIN_SETTINGS = {
    'input_directory': os.path.join(BASE_DIR, 'data/input'),  # Path to directory containing repositories to classify
    'output_directory': os.path.join(BASE_DIR, 'data/output'),  # Path for the output directory
    'model_path': os.path.join(BASE_DIR, 'graph_classification_model.pt'),  # Trained classification model
    'threshold':0.5 # Value above label is considered predicted by model
}

# Graph Class Configuration
GRAPH_SETTINGS = {
    'defined_labels': ['Application', 'Framework', 'Library', 'Plugin'],
}

# Combine all settings into a single dictionary for easy access
CONFIG = {
    'training': TRAINING_SETTINGS,
    'dataset_preparation': DATASET_PREPARATION_SETTINGS,
    'main': MAIN_SETTINGS,
    'graph': GRAPH_SETTINGS,
}
