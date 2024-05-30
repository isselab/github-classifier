from torch.nn import Linear
import torch.nn.functional as F
from GCN_Layer import GCNConv
from torch_geometric.nn import global_mean_pool
import torch

class GCN(torch.nn.Module):
    def __init__(self, num_node_features, num_classes, hidden_channels):
        super(GCN, self).__init__()
        torch.manual_seed(12345)
        # input: number of features per node
        self.conv1 = GCNConv(num_node_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        # number of classes we want to predict
        self.lin = Linear(hidden_channels, num_classes)

    '''add self-loop to edge info? keeps appearing in tutorials
       x=[N, 1] N=number of nodes, x is feature vector
       edge_index=[2, E] E=number of edges, edge_index is adjacency list'''
    def forward(self, x, edge_index):  # runs sigle iteration of a forward pass, orig edge_index
        # obtain node embeddings
        x = self.conv1(x, edge_index)
        x = x.relu()  # relu for non-linearity
        x = self.conv2(x, edge_index)
        x = x.relu()
        x = self.conv3(x, edge_index)

        # readout layer
        # what is batch parameter? appears only in testing i think
        #x = global_mean_pool(x, batch)  # [batch_size, hidden_channels]

        # apply a final classifier
        # dropout for regularization
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.lin(x)

        return x
