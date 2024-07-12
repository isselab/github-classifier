import torch.nn.functional as F
from torch_geometric.nn import GATConv
from torch_geometric.nn import global_mean_pool
import torch

'''defines the architecture of the graph convolutional network'''
class GCN(torch.nn.Module):
    def __init__(self, num_node_features, num_classes, hidden_channels):
        super(GCN, self).__init__()
        torch.manual_seed(12345)
        self.conv1 = GATConv(num_node_features, hidden_channels)
        self.conv2 = GATConv(hidden_channels, hidden_channels)
        self.conv3 = GATConv(hidden_channels, num_classes)

    '''x is node feature matrix with shape x=[N, 11], N=number of nodes
       edge_index is sparse edge matrix with shape edge_index=[2, E], E=number of edges
       edge_attr is edge attribute matrix with shape edge_attr=[E, 17], E=number of edges'''
    def forward(self, x, edge_index, edge_attr, batch=None):  #runs single iteration of a forward pass
        x = self.conv1(x, edge_index, edge_attr)
        x = x.relu()  #relu for non-linearity
        x = self.conv2(x, edge_index, edge_attr)
        x = x.relu()
        x = self.conv3(x, edge_index, edge_attr)
        x = x.relu()

        #readout layer
        x = global_mean_pool(x, batch)

        #dropout for regularization
        x = F.dropout(x, p=0.5, training=self.training)
        #sigmoid activation function for multi-label
        x = F.sigmoid(x)

        return x