import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Profile.css';

const Profile = () => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    firstName: '',
    lastName: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        firstName: user.first_name || '',
        lastName: user.last_name || ''
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/profiles/${user.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user: {
            username: formData.username,
            email: formData.email,
            first_name: formData.firstName,
            last_name: formData.lastName
          }
        })
      });

      if (response.ok) {
        setMessage('Perfil atualizado com sucesso!');
      } else {
        const errorData = await response.json();
        setMessage('Erro ao atualizar perfil: ' + (errorData.detail || 'Erro desconhecido'));
      }
    } catch (error) {
      setMessage('Erro ao atualizar perfil: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="profile">
        <div className="loading">
          <p>Carregando perfil...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile">
      <div className="profile-header">
        <h1>Meu Perfil</h1>
        <p>Gerencie suas informações pessoais</p>
      </div>

      <div className="profile-content">
        <div className="profile-info">
          <h2>Informações da Conta</h2>
          <div className="info-grid">
            <div className="info-item">
              <label>Tipo de Usuário:</label>
              <span className={`user-type ${user.profile?.user_type}`}>
                {user.profile?.user_type === 'admin' ? 'Administrador' : 'Leitor'}
              </span>
            </div>
            {user.profile?.is_admin && (
              <div className="info-item">
                <label>Privilégios:</label>
                <span className="privileges">
                  {user.profile.is_superuser ? 'Super Usuário' : 'Administrador'}
                </span>
              </div>
            )}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="profile-form">
          <h2>Editar Informações</h2>
          
          <div className="form-group">
            <label htmlFor="username">Nome de Usuário:</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="firstName">Primeiro Nome:</label>
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="lastName">Sobrenome:</label>
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
            />
          </div>

          {message && (
            <div className={`message ${message.includes('sucesso') ? 'success' : 'error'}`}>
              {message}
            </div>
          )}

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Atualizando...' : 'Atualizar Perfil'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Profile;