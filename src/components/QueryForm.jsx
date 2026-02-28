import { useState } from "react";
import { queryIssue } from "../api/api";
import  "../styles/app.css"
export default function QueryForm({ setResponse }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    setLoading(true);
    const data = await queryIssue(query);
    // include the original search query so downstream components can include it in escalations
    setResponse({ ...data, search_query: query });
    setLoading(false);
  };

  return (
    <div className="query-box">
      <textarea
        placeholder="Describe the issue (e.g. Finacle login Issue)"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleSubmit}>
        {loading ? "Checking..." : "Resolve Issue"}
      </button>
    </div>
  );
}
