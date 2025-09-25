import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './NewsDetail.css';

const NewsDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchArticle();
  }, [id]);

  const fetchArticle = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:9000/api/news/${id}/`);
      
      if (!response.ok) {
        throw new Error('Notícia não encontrada');
      }
      
      const data = await response.json();
      setArticle(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div className="news-detail">
        <div className="loading">
          <div className="spinner"></div>
          <p>Carregando notícia...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="news-detail">
        <div className="error">
          <h2>Erro ao carregar notícia</h2>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={fetchArticle} className="retry-btn">
              Tentar novamente
            </button>
            <button onClick={handleGoBack} className="back-btn">
              Voltar
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="news-detail">
        <div className="not-found">
          <h2>Notícia não encontrada</h2>
          <p>A notícia que você está procurando não existe ou foi removida.</p>
          <button onClick={handleGoBack} className="back-btn">
            Voltar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="news-detail">
      <div className="news-detail-header">
        <button onClick={handleGoBack} className="back-btn">
          ← Voltar
        </button>
      </div>

      <article className="news-detail-content">
        <header className="article-header">
          <div className="article-category">
            {article.category?.name}
          </div>
          
          <h1 className="article-title">{article.title}</h1>
          
          {article.summary && (
            <p className="article-summary">{article.summary}</p>
          )}
          
          <div className="article-meta">
            <div className="meta-item">
              <span className="meta-label">Publicado em:</span>
              <span className="meta-value">{formatDate(article.published_at)}</span>
            </div>
            
            {article.author?.username && (
              <div className="meta-item">
                <span className="meta-label">Autor:</span>
                <span className="meta-value">{article.author.username}</span>
              </div>
            )}
            
            {article.source && (
              <div className="meta-item">
                <span className="meta-label">Fonte:</span>
                <span className="meta-value">{article.source}</span>
              </div>
            )}
          </div>
        </header>
        
        <div className="article-content">
          <div className="content-text">
            {article.content.split('\n').map((paragraph, index) => (
              <p key={index}>{paragraph}</p>
            ))}
          </div>
        </div>
        
        <footer className="article-footer">
          <div className="article-actions">
            <button onClick={handleGoBack} className="back-btn-footer">
              ← Voltar às notícias
            </button>
          </div>
        </footer>
      </article>
    </div>
  );
};

export default NewsDetail;