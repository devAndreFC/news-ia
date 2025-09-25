import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import './Layout.css';

const Layout = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Verificar se há token no localStorage
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user_data');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    setUser(null);
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
            
            {user && user.profile?.is_admin && (
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