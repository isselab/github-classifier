from torch_geometric.nn import GCNConv
import torch
from torch.nn.parameter import Parameter
import math

class GCNConv(torch.nn.Module):
    def __init__(self, in_features, out_features):
        super(GCNConv, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = Parameter(torch.FloatTensor(in_features, out_features))
        self.reset_parameters()

    def reset_parameters(self):
        stdv = 1. / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        #if self.bias is not None:
           # self.bias.data.uniform_(-stdv, stdv)

    def forward(self, input, adj):
        output = torch.spmm(input, adj)
        #support = torch.mm(input, self.weight)
        #output = torch.spmm(adj, support)
        #if self.bias is not None:
           # return output + self.bias
        #else:
        return output