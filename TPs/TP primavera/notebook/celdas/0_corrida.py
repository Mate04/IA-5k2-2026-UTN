import hashlib
import json
import platform
import random
import time
import uuid

import numpy as np
import torch
import transformers

SEMILLA = 0
random.seed(SEMILLA); np.random.seed(SEMILLA); torch.manual_seed(SEMILLA)
T_INICIO = time.time()
RUN_ID = time.strftime("%Y%m%d-%H%M%S", time.gmtime()) + "-" + uuid.uuid4().hex[:6]
TIEMPOS_FASE = {}            # fase -> segundos desde el inicio (se completa a lo largo de la notebook)

def huella(obj):
    """Hash corto y estable de una configuración: SHA-256 del JSON con las claves ordenadas."""
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:12]

def marcar_fase(nombre):
    TIEMPOS_FASE[nombre] = round(time.time() - T_INICIO, 1)

VERSIONES = dict(python=platform.python_version(), torch=torch.__version__, transformers=transformers.__version__,
                 numpy=np.__version__, cuda=torch.version.cuda,
                 gpu=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
print("RUN_ID:", RUN_ID, "| semilla:", SEMILLA)
print(json.dumps(VERSIONES, ensure_ascii=False))
