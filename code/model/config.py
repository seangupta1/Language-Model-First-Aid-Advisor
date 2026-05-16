from dataclasses import dataclass

@dataclass
class GPTConfig:
    vocab_size: int = 24_000
    context_length: int = 512
    emb_dim: int = 512
    n_heads: int = 8
    n_layers: int = 8
    drop_rate: float = 0.1
    qkv_bias: bool = True