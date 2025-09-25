import { useState, useEffect } from 'react';
import './Admin.css';

const Admin = () => {
  const [stats, setStats] = useState({
    totalNews: 0,
    totalCategories: 0,
    totalUsers: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      // Buscar estatísticas básicas
      const [newsResponse, categoriesResponse] = await Promise.all([
        fetch('http://localhost:9000/api/news/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }),
        fetch('http://localhost:9000/api/categories/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      ]);

      const newsData = await newsResponse.json();
      const categoriesData = await categoriesResponse.json();

      setStats({
        totalNews: newsData.count || newsData.length || 0,
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
            <button className="action-btn">
              Acessar
            </button>
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
    </div>
  );
};

export default Admin;