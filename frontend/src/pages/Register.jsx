import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Login.css'; // Reutilizando os estilos do Login

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: ''
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

    // Validações
    if (formData.password !== formData.confirmPassword) {
      setError('As senhas não coincidem');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres');
      setLoading(false);
      return;
    }

    try {
      // Registrar usuário
      const response = await fetch('http://localhost:9000/api/users/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password
        })
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 400 && data.error?.includes('já existe')) {
          throw new Error('Nome de usuário já está em uso');
        }
        throw new Error(data.error || 'Erro ao criar conta');
      }

      // Buscar dados do usuário usando o token retornado
      const userResponse = await fetch('http://localhost:9000/api/profiles/me/', {
        headers: {
          'Authorization': `Bearer ${data.access_token}`,
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

      // Fazer login automático após registro
      login(userData, {
        access_token: data.access_token,
        refresh_token: data.refresh_token
      });

      // Redirecionar para home (usuários novos são sempre readers)
      navigate('/');
      
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
          <h1>Criar Conta</h1>
          <p>Cadastre-se para acessar o sistema</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Nome de Usuário</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="Digite seu nome de usuário"
              minLength="3"
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
              placeholder="Digite sua senha (mín. 6 caracteres)"
              minLength="6"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmar Senha</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              placeholder="Digite sua senha novamente"
              minLength="6"
            />
          </div>

          <button 
            type="submit" 
            className="login-btn"
            disabled={loading}
          >
            {loading ? 'Criando conta...' : 'Criar Conta'}
          </button>
        </form>

        <div className="login-footer">
          <p>
            Já tem uma conta? 
            <Link to="/login" className="register-link">
              Faça login aqui
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;