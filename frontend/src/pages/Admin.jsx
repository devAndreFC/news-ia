import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import CategoryManager from '../components/CategoryManager';
import './Admin.css';

const Admin = () => {
  const { user, isSuperuser } = useAuth();
  const [stats, setStats] = useState({
    totalNews: 0,
    totalCategories: 0,
    totalUsers: 0
  });
  const [loading, setLoading] = useState(true);
  const [showCategoryManager, setShowCategoryManager] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      // Buscar todas as notícias sem filtros de preferência
      // Fazemos uma requisição com um limite alto para obter todas as notícias
      const [newsResponse, categoriesResponse] = await Promise.all([
        fetch('http://localhost:8000/api/news/?page_size=1000', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }),
        fetch('http://localhost:8000/api/categories/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      ]);

      const newsData = await newsResponse.json();
      const categoriesData = await categoriesResponse.json();

      // Para admin, queremos mostrar TODAS as notícias do sistema
      // Vamos fazer uma segunda requisição para obter o total real
      let totalNewsCount = newsData.count || newsData.length || 0;
      
      // Se o usuário é admin, tentamos obter todas as notícias
      if (user && (user.profile?.is_admin || user.is_superuser)) {
        try {
          // Fazemos uma requisição adicional para tentar obter todas as notícias
          const allNewsResponse = await fetch('http://localhost:8000/api/news/?page_size=10000', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          const allNewsData = await allNewsResponse.json();
          totalNewsCount = allNewsData.count || allNewsData.length || totalNewsCount;
        } catch (adminError) {
          console.log('Usando contagem padrão de notícias');
        }
      }

      setStats({
        totalNews: totalNewsCount,
        totalCategories: categoriesData.count || categoriesData.length || 0,
        totalUsers: 0 // Placeholder
      });
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="admin">
        <div className="loading">
          <div className="spinner"></div>
          <p>Carregando painel administrativo...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin">
      <div className="admin-header">
        <h1>Painel Administrativo</h1>
        <p>Gerencie notícias, categorias e usuários</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📰</div>
          <div className="stat-content">
            <h3>{stats.totalNews}</h3>
            <p>Notícias</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📂</div>
          <div className="stat-content">
            <h3>{stats.totalCategories}</h3>
            <p>Categorias</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>{stats.totalUsers}</h3>
            <p>Usuários</p>
          </div>
        </div>
      </div>

      <div className="admin-actions">
        <h2>Ações Rápidas</h2>
        
        <div className="actions-grid">
          <div className="action-card">
            <h3>📝 Gerenciar Notícias</h3>
            <p>Criar, editar e excluir notícias</p>
            <button className="action-btn">
              Acessar
            </button>
          </div>

          <div className="action-card">
            <h3>📂 Gerenciar Categorias</h3>
            <p>Organizar categorias de notícias</p>
            {isSuperuser() ? (
              <button 
                className="action-btn"
                onClick={() => setShowCategoryManager(true)}
              >
                Acessar
              </button>
            ) : (
              <button className="action-btn disabled" disabled>
                Apenas Superusers
              </button>
            )}
          </div>

          <div className="action-card">
            <h3>👥 Gerenciar Usuários</h3>
            <p>Administrar contas de usuários</p>
            <button className="action-btn">
              Acessar
            </button>
          </div>

          <div className="action-card">
            <h3>📊 Relatórios</h3>
            <p>Visualizar estatísticas detalhadas</p>
            <button className="action-btn">
              Acessar
            </button>
          </div>
        </div>
      </div>
      
      {showCategoryManager && (
        <CategoryManager onClose={() => setShowCategoryManager(false)} />
      )}
    </div>
  );
};

export default Admin;