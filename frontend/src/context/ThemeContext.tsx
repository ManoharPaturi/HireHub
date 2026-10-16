/*
 * Shared light/dark preference. Saving the preference in localStorage keeps
 * it across reloads; the root dark class selects CSS variables in index.css.
 */

import React, { createContext, useContext, useEffect, useState } from 'react';

interface ThemeContextType {
  darkMode: boolean;
  toggleDarkMode: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  darkMode: true,
  toggleDarkMode: () => {},
});

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem('dark_mode');
    return saved !== null ? JSON.parse(saved) : true; // Default to sleek dark mode
  });

  // Apply the saved preference to the document root; CSS variables then
  // change every component using the shared theme tokens.
  useEffect(() => {
    localStorage.setItem('dark_mode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Flip the preference; the effect persists it and updates the root CSS class.
  const toggleDarkMode = () => setDarkMode((prev) => !prev);

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Read the shared theme preference and toggle function.
export const useTheme = () => useContext(ThemeContext);
