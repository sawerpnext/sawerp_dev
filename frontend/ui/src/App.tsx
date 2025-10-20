import { useEffect, useState } from "react";

function App() {
  const [status, setStatus] = useState<string>("Loading...");

  useEffect(() => {
    const base = import.meta.env.VITE_API_BASE as string;
    fetch(`${base}/health/`)
      .then((r) => r.json())
      .then((data) => setStatus(`Backend says: ${data.status}`))
      .catch(() => setStatus("Error contacting backend"));
  }, []);

  return (
    <div style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>ERPShipping</h1>
      <p>{status}</p>
      <p>Frontend (Vite + React + TS) is running.</p>
    </div>
  );
}

export default App;
