import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './NewsManager.css';

const NewsManager = () => {
  const { user } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedNews, setProcessedNews] = useState([]);
  const [dragActive, setDragActive] = useState(false);

  // Verificar se o usuário é admin
  if (!user || (!user.profile?.is_admin && !user.is_superuser)) {
    return (
      <div className="news-manager-container">
        <div className="access-denied">
          <h2>Acesso Negado</h2>
          <p>Apenas administradores podem acessar esta página.</p>
        </div>
      </div>
    );
  }

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/json") {
        setSelectedFile(file);
        setUploadStatus('');
      } else {
        setUploadStatus('Por favor, selecione apenas arquivos JSON.');
      }
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type === "application/json") {
        setSelectedFile(file);
        setUploadStatus('');
      } else {
        setUploadStatus('Por favor, selecione apenas arquivos JSON.');
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Por favor, selecione um arquivo JSON.');
      return;
    }

    setIsProcessing(true);
    setUploadStatus('Processando arquivo...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/news/process-json/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setProcessedNews(result.processed_articles || []);
        setUploadStatus(`Sucesso! ${result.processed_articles?.length || 0} notícias processadas e enviadas para a fila.`);
        setSelectedFile(null);
      } else {
        const error = await response.json();
        setUploadStatus(`Erro: ${error.message || 'Falha no processamento'}`);
      }
    } catch (error) {
      setUploadStatus(`Erro de conexão: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setUploadStatus('');
    setProcessedNews([]);
  };

  return (
    <div className="news-manager-container">
      <div className="news-manager-header">
        <h1>Gerenciar Notícias</h1>
        <p>Faça upload de arquivos JSON para processar e cadastrar notícias automaticamente</p>
      </div>

      <div className="upload-section">
        <div 
          className={`upload-area ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="upload-content">
            <div className="upload-icon">📁</div>
            <h3>Upload de Arquivo JSON</h3>
            <p>Arraste e solte um arquivo JSON aqui ou clique para selecionar</p>
            
            <input
              type="file"
              accept=".json"
              onChange={handleFileSelect}
              className="file-input"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="file-label">
              Selecionar Arquivo
            </label>
          </div>
        </div>

        {selectedFile && (
          <div className="file-info">
            <h4>Arquivo Selecionado:</h4>
            <div className="file-details">
              <span className="file-name">{selectedFile.name}</span>
              <span className="file-size">({(selectedFile.size / 1024).toFixed(2)} KB)</span>
              <button onClick={clearFile} className="clear-btn">✕</button>
            </div>
          </div>
        )}

        <div className="upload-actions">
          <button 
            onClick={handleUpload} 
            disabled={!selectedFile || isProcessing}
            className="upload-btn"
          >
            {isProcessing ? 'Processando...' : 'Processar Arquivo'}
          </button>
        </div>

        {uploadStatus && (
          <div className={`upload-status ${uploadStatus.includes('Erro') ? 'error' : 'success'}`}>
            {uploadStatus}
          </div>
        )}
      </div>

      <div className="info-section">
        <h3>Como funciona o processamento:</h3>
        <div className="process-steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h4>Upload do JSON</h4>
              <p>Envie um arquivo JSON com as notícias a serem processadas</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h4>Análise de Sentimentos</h4>
              <p>O sistema analisa o texto para classificar sentimentos e identificar entidades</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h4>Classificação Automática</h4>
              <p>As notícias são automaticamente categorizadas baseadas no conteúdo</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h4>Fila de Processamento</h4>
              <p>As notícias são enviadas para uma fila RabbitMQ para processamento assíncrono</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">5</div>
            <div className="step-content">
              <h4>Cadastro no Banco</h4>
              <p>Finalmente, as notícias são salvas no banco de dados</p>
            </div>
          </div>
        </div>
      </div>

      <div className="json-format-section">
        <h3>Formato esperado do JSON:</h3>
        <pre className="json-example">
{`{
  "articles": [
    {
      "title": "Título da notícia",
      "content": "Conteúdo completo da notícia...",
      "source": "Nome da fonte",
      "author": "Nome do autor",
      "published_at": "2024-01-15T10:30:00Z"
    }
  ]
}`}
        </pre>
      </div>

      {processedNews.length > 0 && (
        <div className="processed-news-section">
          <h3>Notícias Processadas ({processedNews.length}):</h3>
          <div className="processed-news-list">
            {processedNews.map((news, index) => (
              <div key={index} className="processed-news-item">
                <h4>{news.title}</h4>
                <p><strong>Categoria:</strong> {news.category}</p>
                <p><strong>Sentimento:</strong> {news.sentiment}</p>
                <p><strong>Fonte:</strong> {news.source}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default NewsManager;