import torch
import numpy as np

'''change the shape of the edge tensor to E=[2, number of edges]'''
def convert_edge_dim(edge_tensor):
    edge_tensor = edge_tensor.permute(1,0)
    return edge_tensor

def convert_list_to_tensor(list):
    tensor = torch.LongTensor(np.array(list))
    return tensor