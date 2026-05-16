import math

import torch
import torch.nn as nn

class MultiHeadCausalSelfAttention(nn.Module):
    # Multi-head causal self-attention (scaled dot-product)
    def __init__(self, emb_dim: int, num_heads: int, context_length: int, drop_rate: float, qkv_bias: bool):
        super().__init__()  # init

        assert emb_dim % num_heads == 0  # ensure heads divide embedding dim

        self.emb_dim = emb_dim  # embedding dimension D
        self.num_heads = num_heads  # number of heads H
        self.head_dim = emb_dim // num_heads  # per-head dim

        # Linear projections for Q, K, V (each produces D features)
        self.Wq = nn.Linear(emb_dim, emb_dim, bias=qkv_bias)
        self.Wk = nn.Linear(emb_dim, emb_dim, bias=qkv_bias)
        self.Wv = nn.Linear(emb_dim, emb_dim, bias=qkv_bias)

        # Output projection back to emb_dim
        self.out_proj = nn.Linear(emb_dim, emb_dim, bias=True)

        # Dropout on attention weights
        self.attn_drop = nn.Dropout(drop_rate)

        # Register a causal mask as a non-parameter buffer
        self.register_buffer(
            "mask",
            torch.triu(torch.ones(context_length, context_length, dtype=torch.bool), diagonal=1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, D]
        B, T, D = x.shape  # unpack

        # Project to Q, K, V: [B, T, D]
        Q = self.Wq(x)
        K = self.Wk(x)
        V = self.Wv(x)

        # Reshape into heads: [B, T, D] -> [B, H, T, head_dim]
        Q = Q.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        K = K.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        V = V.view(B, T, self.num_heads, self.head_dim).transpose(1, 2)

        # Scores: [B, H, T, T]
        scores = Q @ K.transpose(-2, -1)

        # Scale scores for stability
        scores = scores / math.sqrt(self.head_dim)

        # Apply causal mask (slice to current T)
        mask = self.mask[:T, :T]
        scores = scores.masked_fill(mask, -torch.inf)

        # Softmax over last dim to get attention weights
        weights = torch.softmax(scores, dim=-1)

        # Apply dropout to attention weights
        weights = self.attn_drop(weights)

        # Context per head: [B, H, T, head_dim]
        context = weights @ V

        # Recombine heads: [B, H, T, head_dim] -> [B, T, D]
        context = context.transpose(1, 2).contiguous().view(B, T, D)

        # Final projection: [B, T, D]
        out = self.out_proj(context)

        return out