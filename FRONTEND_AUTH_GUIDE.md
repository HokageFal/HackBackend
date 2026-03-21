# Руководство по авторизации для фронтенда

## Обзор системы токенов

Система использует два типа токенов:
- **Access Token** - короткоживущий (15 минут), передается в заголовке Authorization
- **Refresh Token** - долгоживущий (15 дней), хранится в HttpOnly cookie

## 1. Вход в систему

```javascript
// POST /users/login
const login = async (email, password) => {
  const response = await fetch('http://localhost:8000/users/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // ВАЖНО: для получения cookies
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Сохраняем access token в памяти (НЕ в localStorage!)
    localStorage.setItem('access_token', data.data.access_token);
    
    // Сохраняем данные пользователя
    localStorage.setItem('user', JSON.stringify(data.data.user));
    
    return data;
  } else {
    // Обработка ошибок
    if (data.errors && data.errors[0]) {
      const error = data.errors[0];
      
      // Специальные сообщения
      if (error.message.includes('заблокирован')) {
        throw new Error('Ваш аккаунт заблокирован. Обратитесь к администратору');
      }
      if (error.message.includes('истек')) {
        throw new Error('Срок доступа к системе истек. Обратитесь к администратору');
      }
      
      throw new Error(error.message);
    }
    throw new Error('Ошибка входа');
  }
};
```

## 2. Автоматическое обновление Access Token

### Вариант A: Перехватчик (Interceptor) - Рекомендуется

```javascript
// axios interceptor
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true // ВАЖНО: для отправки cookies
});

// Добавляем access token к каждому запросу
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Обрабатываем 401 ошибки и обновляем токен
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Если 401 и это не повторный запрос
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Обновляем токен
        const response = await axios.post(
          'http://localhost:8000/users/refresh',
          {},
          { withCredentials: true }
        );
        
        const newAccessToken = response.data.data.access_token;
        localStorage.setItem('access_token', newAccessToken);
        
        // Повторяем оригинальный запрос с новым токеном
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
        
      } catch (refreshError) {
        // Refresh token тоже истек - выходим
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // Проверяем на блокировку или истечение срока
    if (error.response?.data?.errors) {
      const errorMsg = error.response.data.errors[0]?.message || '';
      if (errorMsg.includes('заблокирован') || errorMsg.includes('истек')) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### Вариант B: Fetch с обработкой

```javascript
const fetchWithAuth = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  // Если 401 - пробуем обновить токен
  if (response.status === 401) {
    const refreshResponse = await fetch('http://localhost:8000/users/refresh', {
      method: 'POST',
      credentials: 'include'
    });
    
    if (refreshResponse.ok) {
      const data = await refreshResponse.json();
      const newToken = data.data.access_token;
      localStorage.setItem('access_token', newToken);
      
      // Повторяем запрос с новым токеном
      return fetch(url, {
        ...options,
        credentials: 'include',
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json'
        }
      });
    } else {
      // Refresh не удался - выходим
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      throw new Error('Session expired');
    }
  }
  
  return response;
};
```

## 3. Проактивное обновление токена

Обновляйте токен за 1-2 минуты до истечения:

```javascript
// Декодируем JWT чтобы узнать время истечения
const parseJwt = (token) => {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch (e) {
    return null;
  }
};

// Проверяем и обновляем токен если скоро истечет
const checkAndRefreshToken = async () => {
  const token = localStorage.getItem('access_token');
  if (!token) return;
  
  const decoded = parseJwt(token);
  if (!decoded) return;
  
  const expiresAt = decoded.exp * 1000; // в миллисекунды
  const now = Date.now();
  const timeUntilExpiry = expiresAt - now;
  
  // Если осталось меньше 2 минут - обновляем
  if (timeUntilExpiry < 2 * 60 * 1000) {
    try {
      const response = await fetch('http://localhost:8000/users/refresh', {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.data.access_token);
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
    }
  }
};

// Запускаем проверку каждую минуту
setInterval(checkAndRefreshToken, 60 * 1000);
```

## 4. Выход из системы

```javascript
const logout = async () => {
  try {
    await fetch('http://localhost:8000/users/logout', {
      method: 'POST',
      credentials: 'include'
    });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Очищаем локальное хранилище
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
};
```

## 5. Проверка статуса пользователя

```javascript
// Получаем актуальные данные пользователя
const getCurrentUser = async () => {
  try {
    const response = await api.get('/users/me');
    
    if (response.data.status === 'success') {
      localStorage.setItem('user', JSON.stringify(response.data.data.user));
      return response.data.data.user;
    }
  } catch (error) {
    // Обработка ошибок блокировки/истечения срока
    if (error.response?.data?.errors) {
      const errorMsg = error.response.data.errors[0]?.message || '';
      if (errorMsg.includes('заблокирован')) {
        alert('Ваш аккаунт заблокирован. Обратитесь к администратору');
        logout();
      }
      if (errorMsg.includes('истек')) {
        alert('Срок доступа к системе истек. Обратитесь к администратору');
        logout();
      }
    }
    throw error;
  }
};
```

## 6. React Hook пример

```javascript
import { useEffect, useState } from 'react';
import api from './api'; // axios instance с interceptors

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }
      
      try {
        const response = await api.get('/users/me');
        setUser(response.data.data.user);
      } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
    
    // Проверяем токен каждую минуту
    const interval = setInterval(checkAuth, 60 * 1000);
    return () => clearInterval(interval);
  }, []);
  
  return { user, loading };
};
```

## Важные моменты

1. **Всегда используйте `credentials: 'include'`** - иначе cookies не будут отправляться
2. **Access token в localStorage** - это нормально для SPA, главное не хранить refresh token
3. **Refresh token в HttpOnly cookie** - защищен от XSS атак
4. **CSRF токен больше не нужен** для /users/refresh
5. **Обрабатывайте блокировку и истечение срока** - показывайте понятные сообщения
6. **Используйте interceptors** - это самый надежный способ обновления токенов

## Проверка блокировки/истечения

Бэкенд проверяет при:
- Входе в систему (POST /users/login)
- Каждом запросе психолога (через get_current_psychologist dependency)
- Получении данных пользователя (GET /users/me)

Фронтенд должен:
- Ловить ошибки с кодом 403 (Forbidden)
- Проверять сообщения об ошибках на наличие слов "заблокирован" или "истек"
- Показывать пользователю понятное сообщение
- Выполнять logout и редирект на страницу входа
