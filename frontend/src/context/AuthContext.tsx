import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, adminService } from '../services/api';
import { UserRole } from '../types';

interface AuthUser {
  id: number; email: string; full_name: string;
  role: UserRole; access_token: string;
  avatar_url?: string; gender?: string;
}
interface AuthContextType {
  user: AuthUser | null; isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginAdmin: (email: string, password: string) => Promise<void>;
  register: (payload: any) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const raw = localStorage.getItem('user_info');
    const token = localStorage.getItem('jwt_token');
    if (raw && token) {
      try { setUser(JSON.parse(raw)); } catch { authService.logout(); }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const data = await authService.login(email, password);
    setUser(data);
    localStorage.setItem('user_info', JSON.stringify(data));
  };

  // Separate admin-portal login (/api/admin/login); non-admin accounts are
  // rejected by the backend.
  const loginAdmin = async (email: string, password: string) => {
    const data = await adminService.login(email, password);
    setUser(data);
    localStorage.setItem('user_info', JSON.stringify(data));
  };

  const register = async (payload: any) => {
    const data = await authService.register(payload);
    setUser(data);
    localStorage.setItem('user_info', JSON.stringify(data));
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, loginAdmin, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
