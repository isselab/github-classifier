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
    'output_directory': os.path.join('D:/labeled_repos_output'), # Path to the folder containing the converted repositories
    'labels_file': os.path.join(BASE_DIR, 'data/labeled_dataset_repos.xlsx'),
    'n_epoch': 100,
    'k_folds': 4,  # 1 to disable / Must be at least 2 to be active
    'learning_rate': 0.001,
    'figure_output': os.path.join('C:/Users/const/Documents/Bachelorarbeit/training_testing_plot'), # Local Path used here!!!
    'threshold': 0.5,  # Value above which label is considered predicted by model
    'save_classification_reports': os.path.join(BASE_DIR, 'classification_reports/train.txt'),
    'experiment_name': 'train',
}

# Dataset Preparation Configuration
DATASET_PREPARATION_SETTINGS = {
    'repository_directory': os.path.join('D:/new_15'),  # Path to GitHub repositories , Local Path used here!!!
    'output_directory': os.path.join('D:/new_15_output'), # Local Path used here!!!
    'repository_list_file': os.path.join(BASE_DIR, 'data/new_15.xlsx'),  # Missing?
}

# Main Configuration
MAIN_SETTINGS = {
    'repository_list_file': os.path.join(BASE_DIR, 'data/labeled_dataset_repos.xlsx'),
    'repository_directory': os.path.join(BASE_DIR, 'data/input'),  # Path to directory containing repositories to classify
    'output_directory': os.path.join(BASE_DIR, 'data/output'),  # Path for the output directory
    'path_to_model': os.path.join(BASE_DIR, 'graph_classification_model.pt'),  # Trained classification model
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
