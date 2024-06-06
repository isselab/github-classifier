from torch.nn import Linear
import torch.nn.functional as F
from torch_geometric.nn import GCNConv 
from torch_geometric.nn import global_mean_pool
import torch

'''class GCN defines the architecture of the graph convolutional network'''
class GCN(torch.nn.Module):
    def __init__(self, num_node_features, num_classes, hidden_channels): #hidden channels are filters/number(/dimension) of weight tensors?
        super(GCN, self).__init__()
        torch.manual_seed(12345)
        # input: number of features per node
        self.conv1 = GCNConv(num_node_features, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        self.conv4 = GCNConv(hidden_channels, hidden_channels) #added these two layers to make it overfit hopefully
        self.conv5 = GCNConv(hidden_channels, num_classes)
        # number of classes we want to predict
        #self.lin = Linear(hidden_channels, num_classes) 

    '''add self-loop to edge info? keeps appearing in tutorials
       x=[N, 1] N=number of nodes, x is feature vector
       edge_index=[2, E] E=number of edges, edge_index is adjacency list'''
    def forward(self, x, edge_index, batch):  # runs sigle iteration of a forward pass
        # obtain node embeddings
        x = self.conv1(x, edge_index)
        x = x.relu()  # relu for non-linearity
        x = self.conv2(x, edge_index)
        x = x.relu()
        x = self.conv3(x, edge_index)
        x = x.relu()
        x = self.conv4(x, edge_index)
        x = x.relu()
        x = self.conv5(x, edge_index)

        # readout layer
        x = global_mean_pool(x, batch)  # [batch_size, hidden_channels]

        # apply a final classifier
        # dropout for regularization
        x = F.dropout(x, p=0.5, training=self.training)
        #x = self.lin(x) #maybe softmax instead?
        x = F.log_softmax(x, dim=1)

        return x