import numpy as np
import torch


def convert_edge_dim(edge_tensor):
    """
    Changes the shape of the edge tensor to E=[2, number of edges].

    This function permutes the dimensions of the input edge tensor to rearrange it
    into a format suitable for further processing, where the first dimension represents
    the source and target nodes of the edges.

    Args:
        edge_tensor (torch.Tensor): The input edge tensor to be reshaped.

    Returns:
        torch.Tensor: The reshaped edge tensor with dimensions [2, number of edges].
    """
    edge_tensor = edge_tensor.permute(1, 0)
    return edge_tensor


def convert_list_to_float_tensor(input_list):
    """
    Converts a list to a FloatTensor.

    This function takes a list of numerical values and converts it into a PyTorch
    FloatTensor, which is suitable for use in deep learning models.

    Args:
        input_list (list): The input list containing numerical values.

    Returns:
        torch.FloatTensor: A FloatTensor representation of the input list.
    """
    tensor = torch.FloatTensor(np.array(input_list, dtype=float))
    return tensor


def convert_list_to_long_tensor(input_list):
    """
    Converts a list to a LongTensor.

    This function takes a list of integers and converts it into a PyTorch
    LongTensor, which is useful for representing indices or counts in models.

    Args:
        input_list (list): The input list containing integer values.

    Returns:
        torch.LongTensor: A LongTensor representation of the input list.
      """
    tensor = torch.LongTensor(np.array(input_list, dtype=int))
    return tensor


def convert_hashed_names_to_float(features):
    """
    Converts hex hashes to numerical values.

    This function takes an array of hexadecimal hashes, converts a specific part
    of each hash to a decimal value, and returns a FloatTensor representation of
    the modified features. This is useful for ensuring that the features are fully
    numerical and can be processed by machine learning models.

    Args:
        features (list or np.ndarray): An array of hexadecimal hash values.

    Returns:
        torch.FloatTensor: A FloatTensor representation of the modified features.
    """
    features = np.array(features)
    for hash_value in features:
        helper = hash_value[8]
        dec_hash = int(str(helper), 16)
        dec_hash = dec_hash % 16  # fixed NaN issue with GCN
        hash_value[8] = dec_hash
    tensor = torch.FloatTensor(np.array(features, dtype=float))
    return tensor
