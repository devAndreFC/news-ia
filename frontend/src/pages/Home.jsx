import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [news, setNews] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showOnlyPreferences, setShowOnlyPreferences] = useState(false);
  const [userPreferences, setUserPreferences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    fetchNews();
    fetchCategories();
    if (user) {
      fetchUserPreferences();
    }
  }, [selectedCategory, showOnlyPreferences, user, currentPage]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedCategory, showOnlyPreferences]);

  const fetchNews = async () => {
    try {
      setLoading(true);
      let url = `http://localhost:9000/api/news/?page=${currentPage}`;
      
      if (selectedCategory) {
        url += `&category=${selectedCategory}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Erro ao carregar notícias');
      }
      
      const data = await response.json();
      let newsData = data.results || [];
      
      // Update pagination info
      setTotalCount(data.count || 0);
      setTotalPages(Math.ceil((data.count || 0) / 10)); // 10 items per page
      
      // Filtrar por preferências se ativado (apenas para exibição, não afeta paginação da API)
      if (showOnlyPreferences && userPreferences.length > 0) {
        newsData = newsData.filter(article => 
          article.category && userPreferences.includes(article.category.id)
        );
      }
      
      // Ordenar notícias por data de publicação (mais recentes primeiro)
      const sortedNews = newsData.sort((a, b) => {
        return new Date(b.published_at) - new Date(a.published_at);
      });
      setNews(sortedNews);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:9000/api/categories/');
      if (!response.ok) {
        throw new Error('Erro ao carregar categorias');
      }
      
      const data = await response.json();
      setCategories(data.results || data);
    } catch (err) {
      console.error('Erro ao carregar categorias:', err);
    }
  };

  const fetchUserPreferences = async () => {
    try {
      const response = await fetch('http://localhost:9000/api/profiles/me/preferences/', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setUserPreferences(data.preferred_categories || []);
      }
    } catch (err) {
      console.error('Erro ao carregar preferências:', err);
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

  const handleReadMore = (articleId) => {
    navigate(`/news/${articleId}`);
  };

  if (loading) {
    return (
      <div className="home">
        <div className="loading">
          <div className="spinner"></div>
          <p>Carregando notícias...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="home">
        <div className="error">
          <h2>Erro ao carregar notícias</h2>
          <p>{error}</p>
          <button onClick={fetchNews} className="retry-btn">
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="home">
      <div className="home-header">
        <h1>Últimas Notícias</h1>
        
        <div className="filters">
          <div className="filter-group">
            <label htmlFor="category-filter" className="filter-label">
              Filtrar por categoria:
            </label>
            <select 
              id="category-filter"
              value={selectedCategory} 
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="category-filter"
            >
              <option value="">📰 Todas as categorias</option>
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          {user && userPreferences.length > 0 && (
            <div className="filter-group">
              <button
                onClick={() => setShowOnlyPreferences(!showOnlyPreferences)}
                className={`preferences-filter-btn ${showOnlyPreferences ? 'active' : ''}`}
                title={showOnlyPreferences ? 'Mostrar todas as notícias' : 'Mostrar apenas minhas preferências'}
              >
                {showOnlyPreferences ? '⭐ Minhas Preferências' : '⭐ Filtrar por Preferências'}
              </button>
            </div>
          )}
          
          {(selectedCategory || showOnlyPreferences) && (
            <button 
              onClick={() => {
                setSelectedCategory('');
                setShowOnlyPreferences(false);
              }}
              className="clear-filter-btn"
              title="Limpar todos os filtros"
            >
              ✕ Limpar filtros
            </button>
          )}
        </div>
      </div>

      {(selectedCategory || showOnlyPreferences) && (
        <div className="filter-info">
          <p>
            {selectedCategory && (
              <>
                Exibindo notícias da categoria: <strong>{categories.find(cat => cat.id == selectedCategory)?.name}</strong>
                {showOnlyPreferences && ' '}
              </>
            )}
            {showOnlyPreferences && (
              <>
                {selectedCategory ? 'e ' : 'Exibindo '}
                <strong>apenas suas categorias preferidas</strong>
              </>
            )}
            {news.length > 0 && ` (${news.length} ${news.length === 1 ? 'notícia encontrada' : 'notícias encontradas'})`}
          </p>
        </div>
      )}

      {news.length === 0 ? (
        <div className="no-news">
          <h3>Nenhuma notícia encontrada</h3>
          <p>
            {showOnlyPreferences && selectedCategory 
              ? 'Não há notícias disponíveis para esta categoria em suas preferências no momento.'
              : showOnlyPreferences
              ? 'Não há notícias disponíveis em suas categorias preferidas no momento.'
              : selectedCategory 
              ? 'Não há notícias disponíveis para esta categoria no momento.' 
              : 'Não há notícias disponíveis no momento.'
            }
          </p>
          {showOnlyPreferences && userPreferences.length === 0 && (
            <p>
              <a href="/preferences" style={{color: '#3498db', textDecoration: 'underline'}}>
                Configure suas preferências
              </a> para ver notícias personalizadas.
            </p>
          )}
        </div>
      ) : (
        <div className="news-grid">
          {news.map(article => (
            <article key={article.id} className="news-card">
              <div className="news-card-content">
                <div className="news-header">
                  <h2 className="news-title">{article.title}</h2>
                  {article.category?.name && (
                    <span className="news-category">{article.category.name}</span>
                  )}
                </div>
                
                <div className="news-meta">
                  <span className="news-date">{formatDate(article.published_at)}</span>
                  {article.author?.username && (
                    <span className="news-author">Por {article.author.username}</span>
                  )}
                  {article.source && (
                    <span className="news-source">Fonte: {article.source}</span>
                  )}
                </div>
                
                {article.summary && (
                  <p className="news-summary">{article.summary}</p>
                )}
                
                <div className="news-content">
                  <p>{article.content && article.content.length > 200 
                    ? `${article.content.substring(0, 200)}...` 
                    : article.content || 'Conteúdo não disponível'}
                  </p>
                </div>
                
                <div className="news-actions">
                   <button 
                     className="read-more-btn"
                     onClick={() => handleReadMore(article.id)}
                   >
                     Ler mais
                   </button>
                 </div>
              </div>
            </article>
          ))}
        </div>
      )}

      {/* Pagination Component */}
      {totalPages > 1 && (
        <div className="pagination-footer">
          <div className="pagination-info">
            <span>
              Página {currentPage} de {totalPages} 
              {totalCount > 0 && ` (${totalCount} ${totalCount === 1 ? 'notícia' : 'notícias'} no total)`}
            </span>
          </div>
          
          <div className="pagination-controls">
            <button 
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              className="pagination-btn"
              title="Primeira página"
            >
              ⏮️ Primeira
            </button>
            
            <button 
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="pagination-btn"
              title="Página anterior"
            >
              ⬅️ Anterior
            </button>
            
            <div className="pagination-numbers">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }
                
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`pagination-number ${currentPage === pageNum ? 'active' : ''}`}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>
            
            <button 
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="pagination-btn"
              title="Próxima página"
            >
              Próxima ➡️
            </button>
            
            <button 
              onClick={() => setCurrentPage(totalPages)}
              disabled={currentPage === totalPages}
              className="pagination-btn"
              title="Última página"
            >
              Última ⏭️
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;