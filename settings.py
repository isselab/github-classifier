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
    # Path to the folder containing the converted repositories
    'output_directory': os.path.join('data/output/csv_files'),
    # Path to the Excel file containing labeled dataset information
    'labels_file': os.path.join(BASE_DIR, 'data/labeled_dataset_repos.xlsx'),
    'n_epoch': 50,  # Number of epochs for training the model
    'k_folds': 4,  # Number of folds for k-fold cross-validation; set to 1 to disable, must be at least 2 to be active
    # Learning rate for the optimizer; controls the step size during gradient descent
    'learning_rate': 0.001,
    # Path to save plots generated during training/testing
    'figure_output': os.path.join('data/output/training_test_plot'),
    'threshold': 0.5,  # Value above which label is considered predicted by model in training
    # Path to save classification reports after training
    'save_classification_reports': os.path.join(BASE_DIR, 'classification_reports/train.txt'),
    # Name of the experiment; is used for logging and tracking purposes
    'experiment_name': 'train',
}

# Dataset Preparation Configuration
DATASET_PREPARATION_SETTINGS = {
    # Path to GitHub repositories used as input
    'repository_directory': os.path.join('data/input'),
    # Path to the folder containing the converted repositories
    'output_directory': os.path.join('data/output'),
    # Path to the Excel file containing labeled dataset information
    'repository_list_file': os.path.join(BASE_DIR, 'data/labeled_dataset_repos.xlsx'),
    # Boolean flag; True -> Download all repos from repository_list_files; False -> Do not download from repository_list
    'download_from_repository_list': False
}

# Main Configuration
MAIN_SETTINGS = {
    # Path to directory containing repositories to classify
    'input_directory': os.path.join(BASE_DIR, 'data/input'),
    # Path for the output directory
    'output_directory': os.path.join(BASE_DIR, 'data/output/xmi_files'),
    # Trained classification model
    'model_path': os.path.join(BASE_DIR, 'graph_classification_model.pt'),
    'threshold': 0.5  # Value above label is considered predicted by model
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
