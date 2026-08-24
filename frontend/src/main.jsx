import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

function App() {
  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [score, setScore] = useState(null);
  const [provider, setProvider] = useState("openai");
  const [error, setError] = useState("");

  const load = () =>
    fetch(`${API}/generations`)
      .then((r) => r.json())
      .then(setHistory)
      .catch(() => {});

  useEffect(load, []);

  async function generate() {
    if (!prompt.trim()) return;
    setLoading(true);
    setOutput("");
    setError("");
    try {
      const response = await fetch(`${API}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, provider, use_rag: true, temperature: 0.4 }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Generation failed");
      setOutput(data.output);
      setScore(data.quality_score);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <div>
          <span className="eyebrow">GENFLOW AI</span>
          <h1>Content Intelligence Workspace</h1>
          <p>Generate, validate, evaluate, and refine enterprise content with agentic AI.</p>
        </div>
        <div className="status">● API ready</div>
      </header>

      <section className="grid">
        <div className="card composer">
          <label>CONTENT BRIEF</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe what you want the agent to create..."
          />
          <div className="controls">
            <select value={provider} onChange={(e) => setProvider(e.target.value)}>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
            </select>
            <button onClick={generate} disabled={loading}>
              {loading ? "Running agent…" : "Generate content"}
            </button>
          </div>
        </div>

        <div className="card result">
          <div className="result-head">
            <label>AGENT OUTPUT</label>
            {score !== null && <span className="score">Quality {score}</span>}
          </div>
          {error && <div className="error">{error}</div>}
          <pre>{output || "Your generated content will appear here."}</pre>
        </div>
      </section>

      <section className="card">
        <div className="result-head">
          <label>RECENT GENERATIONS</label>
          <button className="secondary" onClick={load}>Refresh</button>
        </div>
        {history.length === 0 ? (
          <p className="muted">No generations yet.</p>
        ) : (
          history.map((item) => (
            <article className="history" key={item.id}>
              <div>
                <strong>#{item.id}</strong>
                <span>{item.provider} · {item.model} · {item.latency_ms}ms</span>
              </div>
              <p>{item.output}</p>
              <small>Quality {item.quality_score}</small>
            </article>
          ))
        )}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
