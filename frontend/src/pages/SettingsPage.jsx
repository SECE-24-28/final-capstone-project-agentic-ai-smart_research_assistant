import { useTheme } from '../contexts/ThemeContext';

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-6">Settings</h1>
      
      <div className="space-y-6">
        <section className="p-6 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl space-y-4">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">Profile</h2>
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Name</label>
            <input type="text" defaultValue="Dr. Jane Doe" className="w-full p-2 bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)]" />
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Email</label>
            <input type="email" defaultValue="jane@research.org" className="w-full p-2 bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)]" />
          </div>
        </section>

        <section className="p-6 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl space-y-4">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">Appearance</h2>
          <div className="flex items-center justify-between">
            <span className="text-[var(--text-primary)]">Theme</span>
            <button 
              onClick={toggleTheme}
              className="px-4 py-2 bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg text-sm text-[var(--text-primary)] hover:border-[var(--agent-primary)] transition-colors"
            >
              {theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            </button>
          </div>
        </section>

        <section className="p-6 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl space-y-4">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">Account</h2>
          <button className="px-4 py-2 bg-red-500/10 text-red-500 border border-red-500/20 rounded-lg text-sm font-medium hover:bg-red-500/20 transition-colors">
            Logout
          </button>
        </section>
      </div>
    </div>
  );
}
