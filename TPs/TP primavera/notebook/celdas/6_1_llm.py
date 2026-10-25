import os
import difflib
from transformers import AutoTokenizer, AutoModelForCausalLM

# TPI_LLM_ID sólo se usa para probar la plomería en CPU con un modelo más chico; en Kaggle queda el de 3B
LLM_ID = os.environ.get("TPI_LLM_ID", "Qwen/Qwen2.5-3B-Instruct")
LLM_DEVICE = "cuda:1" if torch.cuda.device_count() > 1 else device
LLM_DTYPE = torch.float16 if LLM_DEVICE != "cpu" else torch.float32
torch.manual_seed(0)
tok = AutoTokenizer.from_pretrained(LLM_ID)
tok.padding_side = "left"                     # generación por lotes: el relleno va a la izquierda
try:
    llm = AutoModelForCausalLM.from_pretrained(LLM_ID, dtype=LLM_DTYPE)
except TypeError:                             # versiones de transformers anteriores a `dtype`
    llm = AutoModelForCausalLM.from_pretrained(LLM_ID, torch_dtype=LLM_DTYPE)
llm = llm.to(LLM_DEVICE).eval()
LLM_CONFIG = dict(modelo=LLM_ID, dtype=str(LLM_DTYPE).replace("torch.", ""), decodificacion="greedy", dispositivo=LLM_DEVICE)

@torch.no_grad()
def generar(conversaciones, max_new_tokens=160, lote=8):
    """Generación greedy por lotes. Cada conversación es una lista de mensajes {role, content}."""
    textos = [tok.apply_chat_template(c, tokenize=False, add_generation_prompt=True) for c in conversaciones]
    salidas = []
    for i in range(0, len(textos), lote):
        enc = tok(textos[i:i + lote], return_tensors="pt", padding=True).to(LLM_DEVICE)
        out = llm.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False, repetition_penalty=1.0,
                           pad_token_id=tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id)
        salidas += tok.batch_decode(out[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    return [s.strip() for s in salidas]

t0 = time.time()
prueba_llm = generar([[{"role": "user", "content": "Respondé sólo con la palabra: listo"}]], max_new_tokens=5)
print(json.dumps(LLM_CONFIG), "|", prueba_llm, f"| {time.time() - t0:.1f} s")
