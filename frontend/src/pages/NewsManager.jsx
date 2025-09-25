import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './NewsManager.css';
import { getApiEndpoint } from '../config/api';

const NewsManager = () => {
  const { user } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedNews, setProcessedNews] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [jsonContent, setJsonContent] = useState(null);

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

  // Validação de arquivo JSON
  const validateJsonFile = (file) => {
    return new Promise((resolve, reject) => {
      if (!file) {
        reject('Nenhum arquivo selecionado');
        return;
      }

      if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
        reject('Por favor, selecione um arquivo JSON válido');
        return;
      }

      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        reject('Arquivo muito grande. Limite máximo: 10MB');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const content = JSON.parse(e.target.result);
          if (!Array.isArray(content)) {
            reject('O arquivo JSON deve conter um array de notícias');
            return;
          }
          resolve(content);
        } catch (error) {
          reject('Arquivo JSON inválido: ' + error.message);
        }
      };
      reader.onerror = () => reject('Erro ao ler o arquivo');
      reader.readAsText(file);
    });
  };

  // Funções de drag and drop
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
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = async (file) => {
    try {
      setUploadStatus('');
      const content = await validateJsonFile(file);
      setSelectedFile(file);
      setJsonContent(content);
      setUploadStatus(`Arquivo válido! ${content.length} notícias encontradas.`);
    } catch (error) {
      setUploadStatus(error);
      setSelectedFile(null);
      setJsonContent(null);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setJsonContent(null);
    setUploadStatus('');
    setProcessedNews([]);
  };

  const handleUpload = async () => {
    if (!selectedFile || !jsonContent) {
      setUploadStatus('Nenhum arquivo válido selecionado');
      return;
    }

    setIsUploading(true);
    setUploadStatus('Enviando arquivo para processamento...');

    try {
      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(getApiEndpoint('NEWS_UPLOAD'), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setUploadStatus(`✅ Sucesso! ${result.processed_count || jsonContent.length} notícias enviadas para processamento.`);
        setProcessedNews(result.news || []);
        
        // Limpar após sucesso
        setTimeout(() => {
          clearFile();
        }, 3000);
      } else {
        const error = await response.json();
        setUploadStatus(`❌ Erro: ${error.detail || 'Falha no upload'}`);
      }
    } catch (error) {
      setUploadStatus(`❌ Erro de conexão: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
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
              onChange={(e) => handleFileSelect(e.target.files[0])}
              className="file-input"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="file-label">
              Selecionar Arquivo JSON
            </label>
          </div>
        </div>

        {selectedFile && (
            <div className="file-info">
              <h4>📄 Arquivo Selecionado:</h4>
              <div className="file-details">
                <span className="file-name">{selectedFile.name}</span>
                <span className="file-size">({(selectedFile.size / 1024).toFixed(2)} KB)</span>
                {jsonContent && (
                  <span className="news-count">• {jsonContent.length} notícias</span>
                )}
                <button onClick={clearFile} className="clear-btn">✕</button>
              </div>
            </div>
          )}

        <div className="upload-actions">
          <button 
            onClick={handleUpload} 
            disabled={!selectedFile || !jsonContent || isUploading}
            className="upload-btn"
          >
            {isUploading ? '⏳ Processando...' : '🚀 Processar Notícias'}
          </button>
        </div>

        {uploadStatus && (
          <div className={`upload-status ${
            uploadStatus.includes('✅') || uploadStatus.includes('Sucesso') || uploadStatus.includes('válido') 
              ? 'success' 
              : uploadStatus.includes('❌') || uploadStatus.includes('Erro')
              ? 'error'
              : 'info'
          }`}>
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