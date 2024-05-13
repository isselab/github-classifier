from torch.nn import Linear
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.nn import global_mean_pool
import torch

class GCN(torch.nn.Module):
    def __init__(self, dataset, hidden_channels):
        super(GCN, self).__init__()
        torch.manual_seed(12345)
        self.conv1 = GCNConv(dataset.num_node_features, hidden_channels) #input: number of features per node
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels)
        self.lin = Linear(hidden_channels, dataset.num_classes) #number of classes we want to predict

    #add self-loop to edge info? keeps appearing in tutorials
    #x=[N, 1] N=number of nodes, x is feature vector
    #edge_index=[2, E] E=number of edges, edge_index is adjacency list
    def forward(self, x, edge_index, batch): #runs sigle iteration of a forward pass
        # 1. Obtain node embeddings 
        x = self.conv1(x, edge_index) 
        x = x.relu() #relu for non-linearity
        x = self.conv2(x, edge_index)
        x = x.relu()
        x = self.conv3(x, edge_index)

        # 2. Readout layer
        #what is batch parameter? appears only in testing i think
        x = global_mean_pool(x, batch)  # [batch_size, hidden_channels]

        # 3. Apply a final classifier
        x = F.dropout(x, p=0.5, training=self.training) #dropout for regularization
        x = self.lin(x)
        
        return x