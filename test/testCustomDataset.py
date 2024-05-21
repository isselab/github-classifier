from CustomDataset import RepositoryDataset

'''This file can be executed when it's moved to the folder containing the file CustomDataset.py
It tests whether the dataset can be loaded and sample pairs can be retrieved from the dataset.'''

output_directory = 'D:/tool_output'

print('----------------load dataset------------------')
try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files')
    print('Dataset size: ')
    print(dataset.__len__())
    print('Number of classes: ')
    print(dataset.num_classes)
    print('Sample pair (graph, label): ')
    print(dataset.__getitem__(1))
except Exception as e:
    print(e)
    print('The dataset cannot be loaded.')