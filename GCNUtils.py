import numpy as np

'''i definitely need to permute the edges to fit the dimensions needed of the input, 
not sure about four dim in general,
found info only for 2d convolution'''
def prepare_input_data(node_tensor, edge_tensor, batch_size, hidden_channels):
    N = len(node_tensor)
    #reshaped_nodes = node_tensor.reshape([batch_size, N, 1, hidden_channels]) #nodes only have 1 feature (their type)
    E = len(edge_tensor)
    permuted_edges = edge_tensor.permute(1,0)
    #permuted_edges = permuted_edges.reshape([batch_size, 2, E, hidden_channels])
    #return reshaped_nodes, permuted_edges
    return node_tensor, permuted_edges

# normalize to avoid bias with node types
def normalize_matrix(matrix):
        norm = np.linalg.norm(matrix)
        normalized_matrix = matrix/norm
        return normalized_matrix

'''maybe/preferably call normalize matrix in prepare input data'''