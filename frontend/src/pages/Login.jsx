import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:9000/auth/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (!response.ok) {
        // Padronizar mensagem de erro para credenciais inválidas
        if (response.status === 401) {
          throw new Error('Usuário ou senha inválidos');
        }
        throw new Error(data.detail || data.error || 'Erro ao fazer login');
      }

      // Buscar dados do usuário usando o token
      const userResponse = await fetch('http://localhost:9000/api/profiles/me/', {
        headers: {
          'Authorization': `Bearer ${data.access}`,
          'Content-Type': 'application/json',
        }
      });

      if (!userResponse.ok) {
        throw new Error('Erro ao buscar dados do usuário');
      }

      const profileData = await userResponse.json();

      // Criar objeto de usuário compatível com o contexto
      const userData = {
        ...profileData.user,
        profile: {
          is_admin: profileData.user_type === 'admin',
          user_type: profileData.user_type,
          preferred_categories: profileData.preferred_categories
        }
      };

      // Usar o contexto para fazer login
      login(userData, {
        access_token: data.access,
        refresh_token: data.refresh
      });

      // Redirecionar baseado no tipo de usuário
      if (userData.profile.is_admin) {
        navigate('/admin');
      } else {
        navigate('/');
      }
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>Entrar</h1>
          <p>Acesse sua conta para continuar</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Usuário</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="Digite seu nome de usuário"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Digite sua senha"
            />
          </div>

          <button 
            type="submit" 
            className="login-btn"
            disabled={loading}
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <div className="login-footer">
          <p>
            Não tem uma conta? 
            <Link to="/register" className="register-link">
              Cadastre-se aqui
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;