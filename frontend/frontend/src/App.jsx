import { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

function App() {
  const [papers, setPapers] = useState([])
  const [query, setQuery] = useState('')
  const [uploadFile, setUploadFile] = useState(null)

  useEffect(() => {
    fetchPapers()
  }, [])

  async function fetchPapers() {
    const response = await axios.get(`${API_BASE}/search/papers`)
    setPapers(response.data)
  }

  async function addPaper() {
    if (!query) return
    await axios.post(`${API_BASE}/search/paper`, {
      title: query,
      authors: null,
      abstract: null,
      year: null,
      doi: null,
      journal: null,
      source: 'manual',
    })
    setQuery('')
    fetchPapers()
  }

  async function uploadPdf() {
    if (!uploadFile) return
    const formData = new FormData()
    formData.append('file', uploadFile)
    await axios.post(`${API_BASE}/upload/pdf`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    setUploadFile(null)
    fetchPapers()
  }

  return (
    <div className="app-shell">
      <header>
        <h1>IEEE Research Assistant</h1>
      </header>

      <section className="panel">
        <h2>Paper Search / Add</h2>
        <div className="controls">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Enter paper title or query"
          />
          <button onClick={addPaper}>Add Paper</button>
        </div>
      </section>

      <section className="panel">
        <h2>Upload PDF</h2>
        <div className="controls">
          <input type="file" accept="application/pdf" onChange={(event) => setUploadFile(event.target.files?.[0])} />
          <button onClick={uploadPdf}>Upload PDF</button>
        </div>
      </section>

      <section className="panel">
        <h2>Saved Papers</h2>
        <div className="paper-list">
          {papers.length === 0 && <p>No paper records found.</p>}
          {papers.map((paper) => (
            <article key={paper.id} className="paper-card">
              <strong>{paper.title}</strong>
              <p>{paper.authors || 'Unknown authors'}</p>
              <span>{paper.journal || paper.source || 'No source'}</span>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

export default App
