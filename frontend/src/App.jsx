import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AgentProvider } from './contexts/AgentContext';

import MainLayout from './components/layout/MainLayout';
import ChatPage from './pages/ChatPage';
import LibraryPage from './pages/LibraryPage';
import ReportsPage from './pages/ReportsPage';
import EmailPage from './pages/EmailPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <ThemeProvider>
      <AgentProvider>
        <Router>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<ChatPage />} />
              <Route path="library" element={<LibraryPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="email" element={<EmailPage />} />
              <Route path="settings" element={<SettingsPage />} />
            </Route>
          </Routes>
        </Router>
      </AgentProvider>
    </ThemeProvider>
  );
}

export default App;
