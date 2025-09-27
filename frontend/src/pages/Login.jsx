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
      // Primeiro, fazer login para obter tokens
      const loginResponse = await fetch('http://localhost:8000/auth/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const loginData = await loginResponse.json();

      if (!loginResponse.ok) {
        // Padronizar mensagem de erro para credenciais inválidas
        if (loginResponse.status === 401) {
          throw new Error('Usuário ou senha inválidos');
        }
        throw new Error(loginData.detail || loginData.error || 'Erro ao fazer login');
      }

      // Agora buscar dados do usuário usando o token
      const userResponse = await fetch('http://localhost:8000/api/profiles/me/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${loginData.access}`,
          'Content-Type': 'application/json',
        }
      });

      const userData = await userResponse.json();

      if (!userResponse.ok) {
        throw new Error('Erro ao buscar dados do usuário');
      }

      // Criar objeto de usuário compatível com o contexto
      const userObject = {
        id: userData.user.id,
        username: userData.user.username,
        email: userData.user.email,
        first_name: userData.user.first_name,
        last_name: userData.user.last_name,
        profile: {
          is_admin: userData.user_type === 'admin',
          is_superuser: userData.user.is_superuser,
          user_type: userData.user_type,
          preferred_categories: userData.preferred_categories
        }
      };

      // Usar o contexto para fazer login
      login(userObject, {
        access_token: loginData.access,
        refresh_token: loginData.refresh
      });

      // Redirecionar baseado no tipo de usuário
      if (userObject.profile.is_admin) {
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