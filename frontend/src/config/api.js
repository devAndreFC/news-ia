// Configuração centralizada da API
const API_CONFIG = {
  // Use 127.0.0.1 em vez de localhost para evitar problemas de DNS/proxy
  BASE_URL: 'http://127.0.0.1:8000/api',
  
  // Endpoints específicos
  ENDPOINTS: {
    // Autenticação
    LOGIN: '/users/login/',
    REGISTER: '/users/register/',
    
    // Notícias
    NEWS: '/news/',
    NEWS_UPLOAD: '/news/upload-json/',
    NEWS_ANALYZE: '/news/analyze/',
    NEWS_CLASSIFY: '/news/classify-categories/',
    
    // Categorias
    CATEGORIES: '/categories/',
    
    // Perfis e Preferências
    PROFILES: '/profiles/',
    PROFILE_ME: '/profiles/me/',
    PREFERENCES: '/preferences/',
    PROFILE_PREFERENCES: '/profiles/me/preferences/',
    
    // Admin
    ADMIN_STATS: '/admin/stats/'
  }
};

// Função helper para construir URLs completas
export const buildApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Função helper para construir URLs de endpoints específicos
export const getApiEndpoint = (endpointKey) => {
  const endpoint = API_CONFIG.ENDPOINTS[endpointKey];
  if (!endpoint) {
    throw new Error(`Endpoint '${endpointKey}' não encontrado na configuração`);
  }
  return buildApiUrl(endpoint);
};

export default API_CONFIG;