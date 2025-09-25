import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './CategoryManager.css';

const CategoryManager = ({ onClose }) => {
  const { isSuperuser } = useAuth();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!isSuperuser()) {
      setError('Acesso negado. Apenas superusers podem gerenciar categorias.');
      return;
    }
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/categories/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCategories(data.results || data);
      } else {
        setError('Erro ao carregar categorias');
      }
    } catch (error) {
      console.error('Erro ao carregar categorias:', error);
      setError('Erro ao carregar categorias');
    } finally {
      setLoading(false);
    }
  };

  const generateSlug = (name) => {
    return name
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove acentos
      .replace(/[^a-z0-9\s-]/g, '') // Remove caracteres especiais
      .replace(/\s+/g, '-') // Substitui espaços por hífens
      .replace(/-+/g, '-') // Remove hífens duplicados
      .trim('-'); // Remove hífens no início e fim
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.name.trim()) {
      setError('Nome da categoria é obrigatório');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const slug = generateSlug(formData.name);
      
      const payload = {
        name: formData.name.trim(),
        slug: slug,
        description: formData.description.trim()
      };

      const url = editingCategory 
        ? `http://localhost:8000/api/categories/${editingCategory.id}/`
        : 'http://localhost:8000/api/categories/';
      
      const method = editingCategory ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        setSuccess(editingCategory ? 'Categoria atualizada com sucesso!' : 'Categoria criada com sucesso!');
        setFormData({ name: '', description: '' });
        setEditingCategory(null);
        setShowForm(false);
        fetchCategories();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || errorData.name?.[0] || 'Erro ao salvar categoria');
      }
    } catch (error) {
      console.error('Erro ao salvar categoria:', error);
      setError('Erro ao salvar categoria');
    }
  };

  const handleEdit = (category) => {
    setEditingCategory(category);
    setFormData({
      name: category.name,
      description: category.description || ''
    });
    setShowForm(true);
    setError('');
    setSuccess('');
  };

  const handleDelete = async (categoryId) => {
    if (!confirm('Tem certeza que deseja excluir esta categoria?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/categories/${categoryId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSuccess('Categoria excluída com sucesso!');
        fetchCategories();
      } else {
        setError('Erro ao excluir categoria');
      }
    } catch (error) {
      console.error('Erro ao excluir categoria:', error);
      setError('Erro ao excluir categoria');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingCategory(null);
    setFormData({ name: '', description: '' });
    setError('');
    setSuccess('');
  };

  if (!isSuperuser()) {
    return (
      <div className="category-manager">
        <div className="category-manager-header">
          <h2>Gerenciar Categorias</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="error-message">
          Acesso negado. Apenas superusers podem gerenciar categorias.
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="category-manager">
        <div className="category-manager-header">
          <h2>Gerenciar Categorias</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="loading">
          <div className="spinner"></div>
          <p>Carregando categorias...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="category-manager">
      <div className="category-manager-header">
        <h2>Gerenciar Categorias</h2>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="category-manager-actions">
        <button 
          className="btn-primary" 
          onClick={() => setShowForm(true)}
          disabled={showForm}
        >
          + Nova Categoria
        </button>
      </div>

      {showForm && (
        <div className="category-form">
          <h3>{editingCategory ? 'Editar Categoria' : 'Nova Categoria'}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="name">Nome da Categoria *</label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Digite o nome da categoria"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Descrição</label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Digite uma descrição para a categoria (opcional)"
                rows="3"
              />
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary">
                {editingCategory ? 'Atualizar' : 'Criar'}
              </button>
              <button type="button" className="btn-secondary" onClick={handleCancel}>
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="categories-list">
        <h3>Categorias Existentes ({categories.length})</h3>
        {categories.length === 0 ? (
          <p className="no-categories">Nenhuma categoria encontrada.</p>
        ) : (
          <div className="categories-grid">
            {categories.map((category) => (
              <div key={category.id} className="category-card">
                <div className="category-info">
                  <h4>{category.name}</h4>
                  <p className="category-slug">Slug: {category.slug}</p>
                  {category.description && (
                    <p className="category-description">{category.description}</p>
                  )}
                  <p className="category-stats">
                    {category.news_count || 0} notícias
                  </p>
                </div>
                <div className="category-actions">
                  <button 
                    className="btn-edit" 
                    onClick={() => handleEdit(category)}
                    disabled={showForm}
                  >
                    Editar
                  </button>
                  <button 
                    className="btn-delete" 
                    onClick={() => handleDelete(category.id)}
                    disabled={showForm}
                  >
                    Excluir
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CategoryManager;