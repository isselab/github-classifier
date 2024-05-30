def prepare_input_data(edge_tensor):
    permuted_edges = edge_tensor.permute(1,0)
    return permuted_edges