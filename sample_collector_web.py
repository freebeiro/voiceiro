from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
import aiofiles
from supabase import create_client
from dotenv import load_dotenv
import base64

app = FastAPI()
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

PHRASES = {
    "kids": {  # 8-15 anos
        "quick": {
            "neutras": [
                "Olá! Eu gosto de brincar.",
                "Hoje está um dia lindo!",
                "A minha cor favorita é azul."
            ],
            "perguntas": [
                "Como te chamas?",
                "Queres brincar comigo?",
                "Qual é o teu animal preferido?"
            ],
            "exclamacoes": [
                "Que fixe!",
                "Adoro chocolate!",
                "Isto é super divertido!"
            ],
            "enfase": [
                "É MESMO giro!",
                "Está SUPER bom!",
                "Foi INCRÍVEL!"
            ]
        }
    },
    "teens": {  # 15-20 anos
        "quick": {
            "neutras": [
                "Hoje vou sair com os amigos.",
                "Gosto muito de música.",
                "As aulas foram interessantes."
            ],
            "perguntas": [
                "Vais à festa no sábado?",
                "Qual é a tua banda favorita?",
                "Já fizeste os trabalhos de casa?"
            ],
            "exclamacoes": [
                "Este filme é incrível!",
                "Adoro esta música!",
                "As férias vão ser espetaculares!"
            ],
            "enfase": [
                "Foi o MELHOR concerto!",
                "Estou SUPER animado!",
                "É MESMO fixe!"
            ]
        }
    },
    "adults": {  # 20+ anos
        "quick": {
            "neutras": [
                "O café está muito bom.",
                "Lisboa é uma cidade linda.",
                "O trabalho hoje foi produtivo."
            ],
            "perguntas": [
                "Como foi a reunião?",
                "Vamos jantar fora hoje?",
                "Já viste as notícias?"
            ],
            "exclamacoes": [
                "Que apresentação fantástica!",
                "Este vinho é excelente!",
                "O projeto foi um sucesso!"
            ],
            "enfase": [
                "É um momento HISTÓRICO!",
                "Foi uma decisão CRUCIAL!",
                "É EXTREMAMENTE importante!"
            ]
        }
    }
}

def get_phrases_for_age(age_group):
    """Retorna frases apropriadas para a idade"""
    if age_group in ["8-10", "10-12", "12-15"]:
        return PHRASES["kids"]
    elif age_group in ["15-20"]:
        return PHRASES["teens"]
    else:
        return PHRASES["adults"]

@app.get("/api/phrases")
async def get_phrases(age: str):
    """Endpoint para obter frases baseadas na idade"""
    return get_phrases_for_age(age)

@app.get("/")
async def get_collection_page():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gravação de Voz PT</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {
                --primary-color: #4285f4;
                --success-color: #34a853;
                --warning-color: #fbbc05;
                --error-color: #ea4335;
                --background-color: #f8f9fa;
                --card-color: #ffffff;
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                background: var(--background-color);
                color: #333;
                padding: 16px;
                max-width: 100%;
                overflow-x: hidden;
            }

            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 0 16px;
            }

            .card {
                background: var(--card-color);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }

            .card:active {
                transform: scale(0.98);
            }

            h1 {
                font-size: 24px;
                margin-bottom: 16px;
                text-align: center;
            }

            select, input {
                width: 100%;
                padding: 12px;
                margin: 8px 0;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                -webkit-appearance: none;
            }

            .button {
                width: 100%;
                padding: 16px;
                border: none;
                border-radius: 8px;
                background: var(--primary-color);
                color: white;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
                -webkit-tap-highlight-color: transparent;
            }

            .button:active {
                background: #3367d6;
            }

            .button.recording {
                background: var(--error-color);
                animation: pulse 1.5s infinite;
            }

            .progress {
                display: flex;
                gap: 4px;
                margin: 16px 0;
                justify-content: center;
            }

            .progress-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #ddd;
                transition: all 0.3s;
            }

            .progress-dot.active {
                background: var(--primary-color);
                transform: scale(1.2);
            }

            .progress-dot.completed {
                background: var(--success-color);
            }

            .phrase-display {
                font-size: 20px;
                text-align: center;
                margin: 24px 0;
                min-height: 60px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .tips {
                background: #e8f0fe;
                padding: 16px;
                border-radius: 8px;
                margin: 16px 0;
                font-size: 14px;
            }

            .tips ul {
                list-style: none;
                margin-left: 0;
            }

            .tips li {
                margin: 8px 0;
                padding-left: 24px;
                position: relative;
            }

            .tips li:before {
                content: '✓';
                position: absolute;
                left: 0;
                color: var(--success-color);
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }

            @media (max-width: 480px) {
                body {
                    padding: 8px;
                }

                .card {
                    padding: 16px;
                }

                h1 {
                    font-size: 20px;
                }

                .phrase-display {
                    font-size: 18px;
                }

                .button {
                    padding: 14px;
                }
            }

            /* Melhorias para iOS */
            @supports (-webkit-touch-callout: none) {
                select, input, button {
                    font-size: 16px;  /* Previne zoom em iOS */
                }
            }

            .current-phrase {
                font-size: 24px;
                text-align: center;
                margin: 20px 0;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .record-button {
                width: 100%;
                padding: 15px;
                font-size: 18px;
                background: #4285f4;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            .record-button.recording {
                background: #ea4335;
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); }
            }
        </style>
    </head>
    <body>
        <div id="welcomeScreen">
            <h1>🎤 Gravação de Voz</h1>
            <select id="gender" required>
                <option value="">Género</option>
                <option value="male">Masculino</option>
                <option value="female">Feminino</option>
            </select>
            
            <select id="age" required>
                <option value="">Idade</option>
                <option value="10-15">10-15 anos</option>
                <option value="15-20">15-20 anos</option>
                <option value="20-30">20-30 anos</option>
                <option value="30-40">30-40 anos</option>
                <option value="40-50">40-50 anos</option>
                <option value="50+">Mais de 50 anos</option>
            </select>
            
            <select id="contributionType" required>
                <option value="">Tipo de contribuição</option>
                <option value="quick">Rápida (2-3 min)</option>
                <option value="regular">Regular (5 min)</option>
                <option value="core">Completa (10 min)</option>
            </select>

            <button onclick="startSession()" class="record-button">Começar</button>
        </div>

        <div id="recordingScreen" style="display:none">
            <div class="current-phrase" id="currentPhrase"></div>
            
            <button onclick="toggleRecording()" class="record-button" id="recordButton">
                🎤 Gravar
            </button>

            <div class="tips">
                <h3>📱 Dicas:</h3>
                <ul>
                    <li>✓ Ambiente silencioso</li>
                    <li>✓ Fala naturalmente</li>
                    <li>✓ 15-20cm do microfone</li>
                </ul>
            </div>
        </div>

        <script>
            let mediaRecorder = null;
            let audioChunks = [];
            let currentPhraseIndex = 0;
            let phrases = [];

            async function startSession() {
                const gender = document.getElementById('gender').value;
                const age = document.getElementById('age').value;
                const type = document.getElementById('contributionType').value;

                if (!gender || !age || !type) {
                    alert('Por favor, preencha todos os campos');
                    return;
                }

                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };

                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const formData = new FormData();
                        formData.append('audio', audioBlob, `${gender}_${age}_${currentPhraseIndex}.wav`);
                        
                        try {
                            await fetch('/upload', {
                                method: 'POST',
                                body: formData
                            });
                            
                            currentPhraseIndex++;
                            if (currentPhraseIndex < phrases.length) {
                                showCurrentPhrase();
                            } else {
                                finishSession();
                            }
                        } catch (error) {
                            console.error('Erro ao enviar áudio:', error);
                        }
                        
                        audioChunks = [];
                    };

                    document.getElementById('welcomeScreen').style.display = 'none';
                    document.getElementById('recordingScreen').style.display = 'block';
                    
                    phrases = getAllPhrases(type);
                    showCurrentPhrase();

                } catch (error) {
                    alert('Por favor, permita o acesso ao microfone');
                }
            }

            function toggleRecording() {
                const button = document.getElementById('recordButton');
                
                if (mediaRecorder.state === 'inactive') {
                    audioChunks = [];
                    mediaRecorder.start();
                    button.textContent = '⏹️ Parar';
                    button.classList.add('recording');
                } else {
                    mediaRecorder.stop();
                    button.textContent = '🎤 Gravar';
                    button.classList.remove('recording');
                }
            }

            function showCurrentPhrase() {
                document.getElementById('currentPhrase').textContent = phrases[currentPhraseIndex];
            }

            function finishSession() {
                document.getElementById('recordingScreen').innerHTML = `
                    <div class="current-phrase">
                        <h2>🎉 Obrigado!</h2>
                        <p>Gravação concluída com sucesso!</p>
                    </div>
                `;
            }

            function getAllPhrases(type) {
                return PHRASES[type].neutras
                    .concat(PHRASES[type].perguntas)
                    .concat(PHRASES[type].exclamacoes)
                    .concat(PHRASES[type].enfase);
            }
        </script>
    </body>
    </html>
    """)

@app.post("/upload")
async def upload_audio(audio: UploadFile = File(...), 
                      age: str = Form(...), 
                      gender: str = Form(...)):
    try:
        # Inicializar Supabase
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Ler conteúdo do áudio
        content = await audio.read()
        
        # Converter para base64
        audio_base64 = base64.b64encode(content).decode()
        
        # Salvar no Supabase
        data = {
            "audio": audio_base64,
            "age": age,
            "gender": gender,
            "filename": audio.filename,
            "created_at": "now()"
        }
        
        result = supabase.table("voice_samples").insert(data).execute()
        
        return {"success": True, "id": result.data[0]["id"]}
        
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 