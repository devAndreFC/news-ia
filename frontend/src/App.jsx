import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Login from './pages/Login';
import Admin from './pages/Admin';
import NewsDetail from './pages/NewsDetail';
import './App.css';

// Componente para rotas protegidas
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const token = localStorage.getItem('access_token');
  const userData = localStorage.getItem('user_data');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  if (requireAdmin && userData) {
    const user = JSON.parse(userData);
    if (!user.profile?.is_admin) {
      return <Navigate to="/" replace />;
    }
  }
  
  return children;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="news/:id" element={<NewsDetail />} />
          <Route path="login" element={<Login />} />
          <Route 
            path="admin" 
            element={
              <ProtectedRoute requireAdmin={true}>
                <Admin />
              </ProtectedRoute>
            } 
          />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;