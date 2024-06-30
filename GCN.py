from torch.nn import Linear
import torch.nn.functional as F
from torch_geometric.nn import GCNConv 
from torch_geometric.nn import global_mean_pool, global_max_pool
import torch

'''class GCN defines the architecture of the graph convolutional network'''
class GCN(torch.nn.Module):
    def __init__(self, num_node_features, num_classes, hidden_channels): #hidden channels are filters/number(/dimension) of weight tensors
        super(GCN, self).__init__()
        torch.manual_seed(12345)
        #input: number of features per node
        self.conv1 = GCNConv(num_node_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, num_classes)
        #self.lin = Linear(hidden_channels, num_classes) #try adding back the linear layer and compare?

    '''x=[N, 1] N=number of nodes, x is feature vector
       edge_index=[2, E] E=number of edges, edge_index is adjacency list'''
    def forward(self, x, edge_index, batch):  # runs single iteration of a forward pass
        #obtain node embeddings
        x = self.conv1(x, edge_index)
        x = x.relu()  #relu for non-linearity
        x = self.conv2(x, edge_index)
        x = x.relu()
        x = self.conv3(x, edge_index)
        x = x.relu()

        # readout layer
        x = global_mean_pool(x, batch)

        # dropout for regularization
        x = F.dropout(x, p=0.5, training=self.training)
        #sigmoid activation function for multi-label
        x = F.sigmoid(x)

        return x