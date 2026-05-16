from .blocks import TransformerBlock
from .layers import LayerNorm

import torch
import torch.nn as nn

class GPTModel(nn.Module):
    def __init__(self, cfg):
        super().__init__()  # init

        self.cfg = cfg  # store cfg

        # Embeddings
        self.tok_emb = nn.Embedding(cfg.vocab_size, cfg.emb_dim)
        self.pos_emb = nn.Embedding(cfg.context_length, cfg.emb_dim)
        self.drop_emb = nn.Dropout(cfg.drop_rate)

        # Transformer blocks
        self.blocks = nn.ModuleList([TransformerBlock(cfg) for _ in range(cfg.n_layers)])

        # Final normalization
        self.final_ln = LayerNorm(cfg.emb_dim)

        # Output head (logits over vocab)
        self.out_head = nn.Linear(cfg.emb_dim, cfg.vocab_size, bias=False)

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        # idx: [B, T]
        B, T = idx.shape  # unpack

        # Token embeddings: [B, T, D]
        tok = self.tok_emb(idx)

        # Positional embeddings: [T, D]
        pos_ids = torch.arange(T, device=idx.device)
        pos = self.pos_emb(pos_ids)

        # Combine + dropout: [B, T, D]
        x = self.drop_emb(tok + pos)

        # Pass through transformer blocks
        for block in self.blocks:
            x = block(x)

        # Final norm
        x = self.final_ln(x)

        # Output logits: [B, T, V]
        logits = self.out_head(x)

        return logits
