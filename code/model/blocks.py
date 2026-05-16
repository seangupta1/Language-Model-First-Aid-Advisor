from .layers import LayerNorm, FeedForward
from .attention import MultiHeadCausalSelfAttention

import torch
import torch.nn as nn

class TransformerBlock(nn.Module):
    # GPT-2 style Pre-LN transformer block: (Attn + FFN) with residual connections
    def __init__(self, cfg):
        super().__init__()  # init

        D = cfg.emb_dim  # embedding dim

        # Pre-LN layers
        self.ln1 = LayerNorm(D)
        self.ln2 = LayerNorm(D)

        # Causal multi-head attention
        self.attn = MultiHeadCausalSelfAttention(
            emb_dim=D,
            num_heads=cfg.n_heads,
            context_length=cfg.context_length,
            drop_rate=cfg.drop_rate,
            qkv_bias=cfg.qkv_bias
        )

        # Feed-forward network
        self.ff = FeedForward(D, cfg.drop_rate)

        # Dropout on residual branches (common in GPT-style)
        self.resid_drop = nn.Dropout(cfg.drop_rate)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, D]

        # Attention block (Pre-LN) + residual
        x = x + self.resid_drop(self.attn(self.ln1(x)))

        # Feed-forward block (Pre-LN) + residual
        x = x + self.resid_drop(self.ff(self.ln2(x)))

        return x