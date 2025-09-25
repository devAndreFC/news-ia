import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Layout.css';

const Layout = () => {
  const { user, logout: authLogout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    authLogout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <Link to="/" className="logo">
            📰 News App
          </Link>
          
          <nav className="nav">
            <Link to="/" className="nav-link">
              Notícias
            </Link>
            
            {user && isAdmin() && (
              <Link to="/admin" className="nav-link">
                Administração
              </Link>
            )}
            
            {user ? (
              <div className="user-menu">
                <span className="user-name">
                  Olá, {user.username}
                </span>
                <button onClick={handleLogout} className="logout-btn">
                  Sair
                </button>
              </div>
            ) : (
              <Link to="/login" className="nav-link login-link">
                Entrar
              </Link>
            )}
          </nav>
        </div>
      </header>
      
      <main className="main-content">
        <Outlet />
      </main>
      
      <footer className="footer">
        <p>&copy; 2024 News App. Todos os direitos reservados.</p>
      </footer>
    </div>
  );
};

export default Layout;