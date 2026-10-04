"use client";

import { useState } from "react";

export default function SQLStudio() {
  const [query, setQuery] = useState("SELECT * FROM datasets LIMIT 10;");
  const [result, setResult] = useState<string | null>(null);

  const handleExecute = () => {
    // Simulate query execution
    setResult("Query executed successfully. Result set: 10 rows");
  };

  return (
    <div className="glass-card rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">SQL Studio</h3>

      <div className="relative">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full h-40 p-4 font-mono text-sm bg-background border rounded-md resize-none"
          placeholder="Enter SQL query..."
        />
      </div>

      <div className="flex gap-2 mt-4">
        <button
          onClick={handleExecute}
          className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90"
        >
          Execute
        </button>
        <button className="px-4 py-2 border rounded-md hover:bg-accent/10">
          Format
        </button>
        <button className="px-4 py-2 border rounded-md hover:bg-accent/10">
          Validate
        </button>
      </div>

      {result && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-800">{result}</p>
        </div>
      )}
    </div>
  );
}
