import torch
import numpy as np

'''change the shape of the edge tensor to E=[2, number of edges]'''
def convert_edge_dim(edge_tensor):
    edge_tensor = edge_tensor.permute(1,0)
    return edge_tensor

def convert_list_to_floattensor(list):
    tensor = torch.FloatTensor(np.array(list))
    return tensor

def convert_list_to_longtensor(list):
    tensor = torch.LongTensor(np.array(list))
    return tensor

def convert_list_to_inttensor(list):
    tensor = torch.IntTensor(np.array(list))
    return tensor