import torch
import torch.nn as nn

class RNNModel(nn.Module):
    def __init__(self, input_size, output_size, hidden_dim, n_layers,
                 drop_out, device):
        super(RNNModel, self).__init__()
        # Defining some parameters
        self.device = device
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        # Defining the layers
        self.rnn = nn.RNN(input_size, hidden_dim, n_layers,
                          batch_first=True, dropout = drop_out)
        self.fc = nn.Linear(hidden_dim, output_size)
    
    def forward(self, x):
        batch_size = x.size(0)
        # Initializing hidden state for first input using method defined below
        hidden = self.init_hidden(batch_size)
        # Passing in the input and hidden state into the model and obtaining outputs
        out, hidden = self.rnn(x, hidden)
        # Reshaping the outputs such that it can be fit into the fully connected layer
        hidden = hidden.contiguous().view(-1, self.hidden_dim)
        hidden = self.fc(hidden)
        return hidden #return last hidden layer instead of out, which is all the hidden layers
    
    def init_hidden(self, batch_size):
        # This method generates the first hidden state of zeros which we'll use in the forward pass
        hidden = torch.zeros(self.n_layers, batch_size,
                             self.hidden_dim).to(self.device)
        return hidden
