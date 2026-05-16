import torch
import torch.nn as nn

class LayerNorm(nn.Module):
    def __init__(self, emb_dim: int, eps: float = 1e-5):
        super().__init__()  # initialize base class

        self.eps = eps  # numerical stability term

        # Learnable parameters: scale (gamma) and shift (beta)
        self.gamma = nn.Parameter(torch.ones(emb_dim))  # [D]
        self.beta = nn.Parameter(torch.zeros(emb_dim))  # [D]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, D]

        # Compute mean over the feature dimension D
        mean = x.mean(dim=-1, keepdim=True)  # [B, T, 1]

        # Compute variance over the feature dimension D
        var = x.var(dim=-1, keepdim=True, unbiased=False)  # [B, T, 1]

        # Normalize
        x_hat = (x - mean) / torch.sqrt(var + self.eps)  # [B, T, D]

        # Scale and shift (broadcast gamma/beta over B and T)
        out = self.gamma * x_hat + self.beta  # [B, T, D]

        return out
    
class FeedForward(nn.Module):
    def __init__(self, emb_dim: int, drop_rate: float):
        super().__init__()  # initialize

        # Two-layer MLP with GELU in between
        self.net = nn.Sequential(
            nn.Linear(emb_dim, 4 * emb_dim),  # expand features
            nn.GELU(),                        # nonlinearity
            nn.Linear(4 * emb_dim, emb_dim),  # project back to emb_dim
            nn.Dropout(drop_rate)             # dropout for regularization
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, D]
        return self.net(x)  # [B, T, D]