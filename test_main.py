import pytest
from fastapi.testclient import TestClient
from main import app, get_document_content, analyze_document

client = TestClient(app)

def test_get_document_content(mocker):
    # Mock para requests.get
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.content = b"<html><body>Documento de teste</body></html>"
    mocker.patch('requests.get', return_value=mock_response)
    
    url = "https://docs.magalu.cloud/docs/network/additional-explanations/subnetpool"
    content = get_document_content(url)
    
    assert content == "Documento de teste"

def test_analyze_endpoint(mocker):
    # Mock para get_document_content e analyze_document
    mocker.patch('main.get_document_content', return_value="Texto de exemplo")
    mock_analyze = mocker.patch('main.analyze_document', return_value={"criterio1": {"pontuacao": 9, "justificativa": "Bom"}})

    response = client.post("/analyze", json={"url": "https://docs.magalu.cloud/docs/network/additional-explanations/subnetpool"})
    
    assert response.status_code == 200
    assert response.json() == {"criterio1": {"pontuacao": 9, "justificativa": "Bom"}}

def test_analyze_endpoint_failure(mocker):
    # Mock para get_document_content e analyze_document
    mocker.patch('main.get_document_content', return_value=None)
    mock_analyze = mocker.patch('main.analyze_document', return_value=None)

    response = client.post("/analyze", json={"url": "https://docs.magalu.cloud/docs/network/additional-explanations/subnetpool"})
    
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to retrieve or parse the document."}
