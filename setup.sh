mkdir llm_pt_voice
cd llm_pt_voice
python -m venv venv
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências básicas primeiro
pip install wheel setuptools
pip install torch torchaudio

# Instalar tokenizers e transformers separadamente
pip install tokenizers --no-binary tokenizers
pip install transformers

# Instalar Tortoise-TTS e suas dependências
pip install numpy scipy
pip install einops>=0.6.0
pip install rotary_embedding_torch
pip install unidecode
pip install inflect
pip install progressbar
pip install tortoise-tts

# Outras dependências
pip install requests beautifulsoup4
pip install python-dotenv fastapi uvicorn