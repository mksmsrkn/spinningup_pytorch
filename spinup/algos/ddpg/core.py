import numpy as np
import torch
from torch import nn
from gym.spaces import Box

class MLP(nn.Module):
    def __init__(self, in_dim, hidden_sizes=(64,64), activation=nn.Tanh,
                 output_activation=None, output_scaler=1):
        super(MLP, self).__init__()
        self.output_scaler = output_scaler
        layers = []
        prev_h = in_dim
        for h in hidden_sizes[:-1]:
            layers.append(nn.Linear(prev_h, h))
            layers.append(activation())
            prev_h = h
        layers.append(nn.Linear(h, hidden_sizes[-1]))
        if output_activation:
            try:
                out = output_activation(-1)
            except:
                out = output_activation()
            layers.append(out)
        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x).squeeze() * self.output_scaler

# Credit: https://discuss.pytorch.org/t/how-do-i-check-the-number-of-parameters-of-a-model/4325/9
def count_vars(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

"""
Actor-Critics
"""
class ActorCritic(nn.Module):
    def __init__(self, state_dim, hidden_sizes=(400,300), activation=nn.ReLU,
                 output_activation=nn.Tanh, action_space=None):
        super(ActorCritic, self).__init__()
        assert isinstance(action_space, Box)
        act_dim = action_space.shape[0]
        act_limit = action_space.high[0]

        self.policy = MLP(state_dim, list(hidden_sizes)+[act_dim], activation,
                      output_activation, output_scaler=act_limit)
        self.q = MLP(state_dim + act_dim, list(hidden_sizes)+[1], activation, None)

    def forward(self, x, a = None):
        pi = self.policy(x)
        if a is None:
            return pi
        else:
            q = self.q(torch.cat([x, a],dim=1))
            q_pi = self.q(torch.cat([x, pi],dim=1))
            return pi, q, q_pi