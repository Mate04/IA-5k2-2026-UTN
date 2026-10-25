import kagglehub
import os
kagglehub.login()  # Te pedirá tu token de Kaggle
path = kagglehub.competition_download('tpi-ia-2026-primavera-comprension-visual-de-escenas')

print("Path to competition files:", path)