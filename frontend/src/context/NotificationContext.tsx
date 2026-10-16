/*
 * Shared notification state for signed-in screens. Alerts are fetched from
 * MySQL through the API, counted by their read flag, and refreshed every 15
 * seconds or when the browser tab regains focus. This uses polling, not sockets.
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import { notificationService } from '../services/api';
import { NotificationItem } from '../types';
import { useAuth } from './AuthContext';

interface NotificationContextType {
  notifications: NotificationItem[];
  unreadCount: number;
  loading: boolean;
  refreshNotifications: () => Promise<void>;
  markAsRead: (id: number) => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType>({} as NotificationContextType);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  // Fetch the signed-in account's alerts; keep loading state separate from
  // the returned records so the UI can indicate an in-flight request.
  const fetchNotifications = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    try {
      const data = await notificationService.getNotifications();
      setNotifications(data);
    } catch (e) {
      console.warn("Failed fetching notifications", e);
    } finally {
      setLoading(false);
    }
  };

  // React effects start background work after rendering. Returning a cleanup
  // function removes the timer/listener when auth changes or this provider unmounts.
  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();
      // Keep the bell fresh: poll while logged in and re-fetch on tab focus.
      const t = setInterval(fetchNotifications, 15000);
      const onFocus = () => fetchNotifications();
      window.addEventListener('focus', onFocus);
      return () => { clearInterval(t); window.removeEventListener('focus', onFocus); };
    } else {
      setNotifications([]);
    }
  }, [isAuthenticated]);

  // Persist the read flag first, then update the matching alert in local state.
  const markAsRead = async (id: number) => {
    try {
      await notificationService.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (e) {
      console.error(e);
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        loading,
        refreshNotifications: fetchNotifications,
        markAsRead,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => useContext(NotificationContext);
