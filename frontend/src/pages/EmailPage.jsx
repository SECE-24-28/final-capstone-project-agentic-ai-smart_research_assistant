export default function EmailPage() {
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-6">Email Report</h1>
      <div className="p-6 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl space-y-4">
        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Select Report</label>
          <select className="w-full p-2 bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)]">
            <option>Latest Literature Review</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1">Email Address</label>
          <input type="email" placeholder="colleague@university.edu" className="w-full p-2 bg-[var(--bg-sidebar)] border border-[var(--border-color)] rounded-lg text-[var(--text-primary)]" />
        </div>
        <button className="w-full py-2 bg-[var(--agent-primary)] text-white rounded-lg font-medium hover:opacity-90 transition-opacity">
          Send Email
        </button>
      </div>
    </div>
  );
}
