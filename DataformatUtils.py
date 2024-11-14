import numpy as np
import torch




def convert_edge_dim(edge_tensor):
    """changes the shape of the edge tensor to E=[2, number of edges]"""
    edge_tensor = edge_tensor.permute(1, 0)
    return edge_tensor


def convert_list_to_floattensor(list):
    tensor = torch.FloatTensor(np.array(list, dtype=float))
    return tensor


def convert_list_to_longtensor(list):
    tensor = torch.LongTensor(np.array(list, dtype=int))
    return tensor





def convert_hashed_names_to_float(features):
    """converts the hex hashes to completely numerical values"""
    features = np.array(features)
    for h, hash in enumerate(features):
        helper = hash[8]
        dec_hash = int(str(helper), 16)
        dec_hash = dec_hash % 16  # fixed nan issue with GCN
        hash[8] = dec_hash
    tensor = torch.FloatTensor(np.array(features, dtype=float))
    return tensor
