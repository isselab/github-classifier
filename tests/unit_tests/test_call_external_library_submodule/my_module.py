from torch_geometric.nn import global_mean_pool
import torch

x = torch.tensor([1,0,0])
global_mean_pool(x)