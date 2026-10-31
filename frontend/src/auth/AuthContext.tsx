import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, apiClient, MOCK_USERS } from '@/api';

export type UserRole = 'admin' | 'staff' | 'customer';

interface AuthContextType {
  user: User | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isMockMode: boolean;
  login: (email: string, password?: string) => Promise<void>;
  logout: () => void;
  setMockRole: (role: UserRole) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const isMockMode = apiClient.getIsMockMode();

  useEffect(() => {
    const initAuth = async () => {
      try {
        if (isMockMode) {
          const savedRole = (localStorage.getItem('bl_mock_role') as UserRole) || 'admin';
          const mockUser = MOCK_USERS[savedRole] || MOCK_USERS.admin;
          setUser(mockUser);
        } else {
          const token = apiClient.getAccessToken();
          if (token) {
            const currentUser = await apiClient.get<User>('/auth/me/');
            setUser(currentUser);
          }
        }
      } catch (err) {
        console.error('Failed initializing auth', err);
        apiClient.clearTokens();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, [isMockMode]);

  const login = async (email: string, password?: string) => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<{ access: string; refresh: string; user: User }>('/auth/login/', {
        email,
        password,
      });
      apiClient.setTokens({ access: res.access, refresh: res.refresh });
      setUser(res.user);
      if (isMockMode) {
        localStorage.setItem('bl_mock_role', res.user.role);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    apiClient.clearTokens();
    if (isMockMode) {
      // In mock mode, keep an unauthenticated state
      setUser(null);
      localStorage.removeItem('bl_mock_role');
    } else {
      setUser(null);
    }
  };

  const setMockRole = (role: UserRole) => {
    localStorage.setItem('bl_mock_role', role);
    const mockUser = MOCK_USERS[role];
    setUser(mockUser);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role: user?.role || null,
        isAuthenticated: !!user,
        isLoading,
        isMockMode,
        login,
        logout,
        setMockRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
