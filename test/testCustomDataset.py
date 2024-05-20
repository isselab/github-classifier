from CustomDataset import RepositoryDataset

'''this file can be executed when it's moved to the folder containing the file CustomDataset.py'''

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