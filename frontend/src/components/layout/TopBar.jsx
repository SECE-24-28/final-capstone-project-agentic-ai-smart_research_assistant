import AgentSelector from '../AgentSelector';
import ThemeToggle from '../ThemeToggle';

export default function TopBar() {
  return (
    <header className="h-14 border-b border-[var(--border-color)] bg-[var(--bg-page)] flex items-center justify-between px-4 shrink-0 transition-colors duration-200">
      <div className="flex items-center gap-2">
        <AgentSelector />
      </div>
      <div className="flex items-center gap-2">
        <ThemeToggle />
      </div>
    </header>
  );
}
