import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import './Preferences.css';

const Preferences = () => {
  const { user } = useAuth();
  const [categories, setCategories] = useState([]);
  const [userPreferences, setUserPreferences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchCategories();
    fetchUserPreferences();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/preferences/');
      if (!response.ok) {
        throw new Error('Erro ao carregar categorias');
      }
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (err) {
      setError('Erro ao carregar categorias: ' + err.message);
    }
  };

  const fetchUserPreferences = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Você precisa estar logado para acessar suas preferências.');
        setLoading(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/profiles/me/preferences/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) {
        if (response.status === 401) {
          setError('Você precisa estar logado para acessar suas preferências.');
        } else {
          throw new Error('Erro ao carregar preferências');
        }
        return;
      }
      const data = await response.json();
      // Extrair apenas os IDs das categorias preferidas
      const preferredIds = (data.preferred_categories || []).map(cat => 
        typeof cat === 'object' ? cat.id : cat
      );
      setUserPreferences(preferredIds);
    } catch (err) {
      setError('Erro ao carregar preferências: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getAuthToken = () => {
    return localStorage.getItem('access_token');
  };

  const handleCategoryToggle = (categoryId) => {
    setUserPreferences(prev => {
      if (prev.includes(categoryId)) {
        return prev.filter(id => id !== categoryId);
      } else {
        return [...prev, categoryId];
      }
    });
  };

  const handleSavePreferences = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const token = getAuthToken();
      if (!token) {
        throw new Error('Você precisa estar logado para salvar preferências');
      }

      const response = await fetch('http://localhost:8000/api/profiles/me/preferences/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          preferred_categories: userPreferences
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erro ao salvar preferências');
      }

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Erro ao salvar preferências: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="preferences">
        <div className="loading">
          <div className="spinner"></div>
          <p>Carregando preferências...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="preferences">
      <div className="preferences-header">
        <h1>⚙️ Minhas Preferências</h1>
        <p>Selecione as categorias de notícias que você deseja ver</p>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          {error.includes('logado') && (
            <p>
              <Link to="/login" className="login-link">
                Clique aqui para fazer login
              </Link>
            </p>
          )}
        </div>
      )}

      {success && (
        <div className="success-message">
          <p>✅ Preferências salvas com sucesso!</p>
        </div>
      )}

      <div className="preferences-content">
        <div className="categories-section">
          <h2>Categorias Disponíveis</h2>
          <p className="section-description">
            Marque as categorias que você tem interesse em acompanhar:
          </p>
          
          <div className="categories-grid">
            {Array.isArray(categories) && categories.map(category => (
              <div key={category.id} className="category-item">
                <label className="category-label">
                  <input
                    type="checkbox"
                    checked={userPreferences.includes(category.id)}
                    onChange={() => handleCategoryToggle(category.id)}
                    className="category-checkbox"
                  />
                  <div className="category-info">
                    <h3 className="category-name">{category.name}</h3>
                    {category.description && (
                      <p className="category-description">{category.description}</p>
                    )}
                    <span className="category-count">
                      {category.news_count} {category.news_count === 1 ? 'notícia' : 'notícias'}
                    </span>
                  </div>
                </label>
              </div>
            ))}
          </div>
        </div>

        <div className="preferences-summary">
          <h3>Resumo das suas preferências</h3>
          {userPreferences.length === 0 ? (
            <p className="no-preferences">
              Nenhuma categoria selecionada. Você verá todas as notícias.
            </p>
          ) : (
            <div className="selected-categories">
              <p>Você selecionou {userPreferences.length} {userPreferences.length === 1 ? 'categoria' : 'categorias'}:</p>
              <ul className="selected-list">
                {userPreferences.map(prefId => {
                  const category = Array.isArray(categories) ? categories.find(cat => cat.id === prefId) : null;
                  return category ? (
                    <li key={prefId} className="selected-item">
                      {category.name}
                    </li>
                  ) : null;
                })}
              </ul>
            </div>
          )}
        </div>

        <div className="preferences-actions">
          <button
            onClick={handleSavePreferences}
            disabled={saving}
            className="save-btn"
          >
            {saving ? '💾 Salvando...' : '💾 Salvar Preferências'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Preferences;