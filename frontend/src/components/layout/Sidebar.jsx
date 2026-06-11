import { NavLink } from 'react-router-dom';
import { MessageSquare, Library, FileText, Mail, Settings, Plus, Beaker } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export default function Sidebar() {
  const recentChats = [
    "Federated Learning Security",
    "Healthcare AI",
    "Edge AI",
    "Cyber Security",
    "Machine Learning"
  ];

  return (
    <div className="w-64 bg-[var(--bg-sidebar)] border-r border-[var(--border-color)] flex flex-col h-full shrink-0 transition-colors duration-200">
      {/* Header */}
      <div className="p-4 flex items-center gap-2 font-semibold text-lg border-b border-[var(--border-color)]">
        <Beaker className="w-6 h-6 text-[var(--agent-primary)] transition-colors duration-300" />
        <span>Smart Research</span>
      </div>

      {/* New Research Button */}
      <div className="p-4">
        <button className="w-full flex items-center gap-2 px-4 py-2 bg-[var(--bg-card)] hover:bg-[var(--border-color)] border border-[var(--border-color)] rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          New Research
        </button>
      </div>

      {/* Navigation */}
      <div className="px-3 space-y-1">
        <NavItem to="/" icon={MessageSquare} label="Chat" />
        <NavItem to="/library" icon={Library} label="Library" />
        <NavItem to="/reports" icon={FileText} label="Reports" />
        <NavItem to="/email" icon={Mail} label="Email" />
      </div>

      {/* Recent Chats (Mock) */}
      <div className="flex-1 overflow-y-auto mt-6 px-3">
        <h3 className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-2 px-3">
          Recent Chats
        </h3>
        <div className="space-y-1">
          {recentChats.map((chat, i) => (
            <div key={i} className="px-3 py-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-card)] rounded-lg cursor-pointer truncate transition-all duration-200 hover:border-l-2 border-[var(--agent-primary)]">
              {chat}
            </div>
          ))}
        </div>
      </div>

      {/* Footer Navigation */}
      <div className="p-3 border-t border-[var(--border-color)] space-y-1">
        <NavItem to="/settings" icon={Settings} label="Settings" />
        
        {/* User Profile */}
        <div className="flex items-center gap-3 px-3 py-3 mt-2 rounded-lg hover:bg-[var(--bg-card)] cursor-pointer transition-colors">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[var(--agent-primary)] to-[var(--agent-secondary)] flex items-center justify-center text-white font-bold text-sm transition-colors duration-300">
            JD
          </div>
          <div className="flex flex-col text-sm truncate">
            <span className="font-medium truncate">Dr. Jane Doe</span>
            <span className="text-xs text-[var(--text-secondary)] truncate">jane@research.org</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function NavItem({ to, icon: Icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => cn(
        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 border-l-2",
        isActive 
          ? "bg-[var(--bg-card)] text-[var(--text-primary)] font-medium border-[var(--agent-primary)] shadow-sm" 
          : "text-[var(--text-secondary)] hover:bg-[var(--bg-card)] hover:text-[var(--text-primary)] border-transparent"
      )}
    >
      <Icon className="w-4 h-4" />
      {label}
    </NavLink>
  );
}
