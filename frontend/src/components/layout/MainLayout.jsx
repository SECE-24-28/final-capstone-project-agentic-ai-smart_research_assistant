import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { useTheme } from '../../contexts/ThemeContext';

export default function MainLayout() {
  const { theme } = useTheme();

  return (
    <div className="flex h-screen bg-[var(--bg-page)] text-[var(--text-primary)] overflow-hidden transition-colors duration-200 relative z-0">
      {theme === "light" && (
        <>
          <div className="agent-bg-blob-primary" />
          <div className="agent-bg-blob-secondary" />
        </>
      )}

      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 z-10 bg-transparent">
        <Outlet />
      </div>
    </div>
  );
}
