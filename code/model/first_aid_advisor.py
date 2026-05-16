import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Literal
from .config import GPTConfig

class FirstAidAdvisorLM():
    def __init__(
            self,
            model_name: Literal['untrained', 'pretrained', 'fine_tuned'] = 'fine_tuned',
            print_details: bool=False
            ):
        self.model_name = model_name
        self.tokenizer = self.load_tokenizer(print_model=print_details)
        self.model = None
        if model_name == 'untrained':
            self.model = self.load_untrained_model(print_model=print_details)
        elif model_name == 'pretrained':
            self.model = self.load_pretrained_model(print_model=print_details)
        else:
            self.model = self.load_fine_tuned_model(print_model=print_details)

    def load_tokenizer(self, print_model: bool=True):
        from pathlib import Path
        from tokenizers import Tokenizer
        
        current_dir = Path(__file__).parent
        tokenizer_path = current_dir / "tokenizer" / "tokenizer.json"
        if not tokenizer_path.exists():
            raise FileNotFoundError(f"Missing file at: {tokenizer_path}")
        
        tokenizer = Tokenizer.from_file(str(tokenizer_path))

        if print_model:
            print("Tokenizer_vocab_size:", tokenizer.get_vocab_size())
            
        return tokenizer

    def print_model_details(self, model, cfg):
        for key, value in vars(cfg).items():
            print(f"{key}: {value}")
        from IPython.display import display, Markdown # Solution for output cutting off
        display(Markdown("```\n" + str(model) + "\n```"))

    def load_untrained_model(self, print_model: bool=True):
        from .config import GPTConfig
        from .gpt import GPTModel
        cfg = GPTConfig()
        model = GPTModel(cfg)
        model = self.MyCausalLMWrapper(model)
        if(print_model):
            self.print_model_details(model, cfg)

        model.eval()
        
        return model

    def load_pretrained_model(self, print_model: bool=True):
        from pathlib import Path
        from torch import load, device
        from .config import GPTConfig
        from .gpt import GPTModel

        cfg = GPTConfig()
        model = GPTModel(cfg)

        current_dir = Path(__file__).parent
        model_path = current_dir / "model_weights" / "pretrained_model_weights.pth"
        if not model_path.exists():
            raise FileNotFoundError(f"Missing file at: {model_path}")

        model.load_state_dict(load(model_path, map_location=device('cpu')))

        model = self.MyCausalLMWrapper(model)

        if(print_model):
            self.print_model_details(model, cfg)

        model.eval()
        
        return model

    class MyCausalLMWrapper(nn.Module):
        def __init__(self, model):
            super().__init__()
            self.model = model

            # Reuse your existing cfg instead of dummy object
            self.config = model.cfg

            # Add required attributes if missing
            self.config.model_type = "gpt2"

            if not hasattr(self.config, "_attn_implementation"):
                setattr(self.config, "_attn_implementation", "eager")

            if not hasattr(self.config, "torch_dtype"):
                setattr(self.config, "torch_dtype", next(model.parameters()).dtype)

        def forward(self, input_ids, labels=None, **kwargs):
            from transformers.modeling_outputs import CausalLMOutput

            logits = self.model(input_ids)

            if labels is not None:
                loss = nn.functional.cross_entropy(
                    logits.view(-1, logits.size(-1)),
                    labels.view(-1)
                )
                return CausalLMOutput(loss=loss, logits=logits)

            return CausalLMOutput(logits=logits)

        def prepare_inputs_for_generation(self, input_ids, **kwargs):
            return {"input_ids": input_ids, **kwargs}

        def add_model_tags(self, tags):
            pass

    def load_fine_tuned_model(self, print_model: bool=True):
        from pathlib import Path
        from peft import PeftModel, PeftConfig

        base_model = self.load_pretrained_model(print_model)
        
        current_dir = Path(__file__).parent
        lora_adapter_path = current_dir / "model_weights" / "sft_lora_adapter"
        if not lora_adapter_path.exists():
            raise FileNotFoundError(f"Missing file at: {lora_adapter_path}")

        # model = MyCausalLMWrapper(base_model)
        model = base_model
        model = PeftModel.from_pretrained(
            model,
            str(lora_adapter_path)
        )

        if print_model:
            config = PeftConfig.from_pretrained(lora_adapter_path)
            print(config)

        model.eval()

        return model
    
    def answer(
            self,
            prompt: str,
            max_new_tokens: int = 64,
            temperature: float = 0.8,
            top_k: int = 50,
            repetition_penalty: float = 1.1,
            device: str = "cpu",
            ):
        self.model.eval()
        self.model.to(device)

        if not isinstance(prompt, str) or not prompt:
            return "Invalid prompt provided."
        
        if self.model_name == 'fine_tuned':
            prompt = self.alpaca_prompt(user_input=prompt)

        # tokenize
        encoded = self.tokenizer.encode(prompt)
        input_ids = torch.tensor([encoded.ids], dtype=torch.long, device=device)
        prompt_length = input_ids.shape[1]

        if prompt_length >= GPTConfig.context_length:
            return f"Prompt is too long. Max length is {GPTConfig.context_length - 1}."

        generated = input_ids

        with torch.no_grad():
            for _ in range(max_new_tokens):

                outputs = self.model(generated)

                logits = outputs.logits[:, -1, :]

                # Repetition penalty
                if repetition_penalty != 1.0:
                    for token_id in set(generated[0].tolist()):
                        logits[0, token_id] /= repetition_penalty

                # Temperature
                logits = logits / temperature

                # Top-k
                if top_k is not None and top_k > 0:
                    values, indices = torch.topk(logits, top_k, dim=-1)
                    probs = F.softmax(values, dim=-1)

                    next_token = indices.gather(
                        -1,
                        torch.multinomial(probs, num_samples=1)
                    )
                else:
                    probs = F.softmax(logits, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)

                # Append token
                generated = torch.cat([generated, next_token], dim=1)

        # Remove prompt from begining of response
        new_tokens = generated[0, prompt_length:]

        return self.tokenizer.decode(
            new_tokens.tolist(),
            skip_special_tokens=True
        )
    
    def alpaca_prompt(self, user_input):
        instruction = "Provide treatment and OTC recommendations for the question."
        input_text = user_input.strip()
        if input_text:
            return f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:
"""
        return f"""### Instruction:
{instruction}

### Response:
"""
