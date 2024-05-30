from torch_geometric.nn import ChebConv
import torch
from torch.nn.parameter import Parameter
import math
import torch.nn as nn
from torch_geometric.nn.conv import MessagePassing

class ChebConv(MessagePassing):
    def __init__(self, in_features, out_features, bias=True): #out_features: size of each output sample
        super(ChebConv, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = nn.Parameter(torch.FloatTensor(torch.zeros(size=(in_features, out_features))))
        if bias:
            self.bias = Parameter(torch.FloatTensor(out_features))
        else:
            self.register_parameter('bias', None)
        self.initialize_weights()
        self.reset_parameters()
        print(self.weight.size())
        

    def initialize_weights(self):
        nn.init.xavier_uniform_(self.weight)
        if self.bias is not None:
            nn.init.zeros_(self.bias)

    def reset_parameters(self):
        stdv = 1. / math.sqrt(self.weight.size(1))
        self.weight.data.uniform_(-stdv, stdv)
        if self.bias is not None:
            self.bias.data.uniform_(-stdv, stdv)

    def forward(self, input, adj):
        super(ChebConv, self)
        support = torch.matmul(input, self.weight) #multiply input with weights, orig torch.mm
        print(support.size())
        output = torch.spmm(adj, support)
        #output = torch.matmul(adj, support)
        if self.bias is not None:
            return output + self.bias
        else:
            return output
        
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=1.0)
            if module.bias is not None:
                module.bias.data.zero_()