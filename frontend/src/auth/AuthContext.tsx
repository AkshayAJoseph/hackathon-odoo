import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, apiClient, MOCK_USERS } from '@/api';

export type UserRole = 'admin' | 'staff' | 'customer';

interface SignupData {
  email: string;
  password: string;
  name: string;
  company?: string;
}

interface AuthResponse {
  access: string;
  refresh: string;
  user?: User;
  id?: number;
  email?: string;
  name?: string;
  role?: UserRole;
  company?: string;
}

interface AuthContextType {
  user: User | null;
  role: UserRole | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isMockMode: boolean;
  login: (email: string, password?: string) => Promise<User>;
  signup: (data: SignupData) => Promise<User>;
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

  const resolveUserFromResponse = (res: AuthResponse, fallbackEmail: string): User => {
    if (res.user) {
      return res.user;
    }
    return {
      id: res.id || 1,
      email: res.email || fallbackEmail,
      name: res.name || fallbackEmail.split('@')[0],
      role: res.role || 'customer',
      company: res.company,
    };
  };

  const login = async (email: string, password?: string): Promise<User> => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<AuthResponse>('/auth/login/', {
        email,
        password,
      });
      apiClient.setTokens({ access: res.access, refresh: res.refresh });
      const authenticatedUser = resolveUserFromResponse(res, email);
      setUser(authenticatedUser);
      if (isMockMode) {
        localStorage.setItem('bl_mock_role', authenticatedUser.role);
      }
      return authenticatedUser;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (data: SignupData): Promise<User> => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<AuthResponse>('/auth/signup/', data);
      apiClient.setTokens({ access: res.access, refresh: res.refresh });
      const newUser = resolveUserFromResponse(res, data.email);
      setUser(newUser);
      if (isMockMode) {
        localStorage.setItem('bl_mock_role', newUser.role);
      }
      return newUser;
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
        signup,
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
