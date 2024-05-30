from torch_geometric.loader import DataLoader
from torch.utils.data import random_split
from CustomDataset import RepositoryDataset

output_directory = 'D:/output'

print('--------------load dataset---------------')

try:
    dataset = RepositoryDataset(f'{output_directory}/csv_files')
except Exception as e:
    print(e)
    print('Dataset cannot be loaded.')

train_dataset, test_dataset = random_split(dataset, [0.7, 0.3])
print(len(train_dataset), len(test_dataset))

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

for step, data in enumerate(train_loader):
    print(f'Step {step + 1}:')
    print('=======')
    print(f'Number of graphs in the current batch: {data.num_graphs}')
    print(data)
    print()
    print(data.edge_index)

class DataLoader():
    def __init__(self, dataset, batch_size, shuffle):
        pass