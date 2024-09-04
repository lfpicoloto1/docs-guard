from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import anthropic

app = FastAPI()

cloud_token = os.getenv('CLOUD_TOKEN')
if cloud_token is None:
    raise ValueError("A variável de ambiente CLOUD_TOKEN não está definida.")

class DocumentRequest(BaseModel):
    url: str

def get_document_content(url):
    
    parsed_url = urlparse(url)
    if parsed_url.scheme == 'https' and 'docs.magalu' in parsed_url.netloc:
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            full_text = soup.get_text(separator='\n', strip=True)
            full_text = re.sub(r'\n\s*\n', '\n\n', full_text)
            return full_text
        except requests.RequestException as e:
            print(f"An error occurred during the HTTP request: {e}")
            return None
    else:
        print("URL does not meet the required criteria.")
        return None

def analyze_document(text, cloud_token):
    criterios = [
        "Clareza",
        "Ortografia",
        "Organização",
        "Precisão técnica"
    ]
    criterios_texto = "\n".join([f"{i+1}. {criterio}" for i, criterio in enumerate(criterios)])
    prompt = f"""Analise a seguinte documentação técnica e compare com outros providers de cloud e atribua uma pontuação de 1 a 10 para cada um dos seguintes critérios, e coloque exemplos de como melhorar na justificativa:
    {criterios_texto}
    Para cada critério, forneça uma breve justificativa para a pontuação atribuída.
    Documentação:
    {text}
    Responda no formato JSON, com a seguinte estrutura:
    {{
        "criterio1": {{"pontuacao": X, "justificativa": "...", }},
        "criterio2": {{"pontuacao": X, "justificativa": "..."}},
        ...
    }}
    Análise:"""

    try:
        client = anthropic.Anthropic(api_key=cloud_token)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        json_text = response.content[0].text

        try:
            data = json.loads(json_text)
            print(json.dumps(data, indent=4, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
        data = json.loads(json_text)
        return data
    
    except Exception as e:
        print(f"An error occurred with the Anthropics API: {e}")
        return None

@app.post("/analyze")
def analyze(request: DocumentRequest):
    url = request.url
    full_text = get_document_content(url)
    if not full_text:
        raise HTTPException(status_code=500, detail="Failed to retrieve or parse the document.")

    result = analyze_document(full_text, cloud_token)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to analyze the document.")

    return result

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")