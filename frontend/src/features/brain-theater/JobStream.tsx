"use client";

import { useEffect, useState, useRef } from "react";

interface JobEvent {
  id: string;
  type: "start" | "progress" | "success" | "error" | "complete";
  agent: string;
  message: string;
  timestamp: string;
  confidence?: number;
  duration_ms?: number;
}

interface JobStreamProps {
  taskId?: string;
  autoConnect?: boolean;
}

export default function JobStream({ taskId = "auto", autoConnect = true }: JobStreamProps) {
  const [events, setEvents] = useState<JobEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [inputQuery, setInputQuery] = useState("");
  const eventsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    eventsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  useEffect(() => {
    if (!autoConnect) return;

    const simulateJob = async () => {
      const mockEvents: JobEvent[] = [
        { id: "1", type: "start", agent: "brain_controller", message: "Received task: Analyze sales data trends", timestamp: new Date().toISOString() },
        { id: "2", type: "progress", agent: "sql_agent", message: "Validating SQL query with gate...", timestamp: new Date().toISOString(), confidence: 0.95 },
        { id: "3", type: "progress", agent: "sql_agent", message: "Executing query on DuckDB engine", timestamp: new Date().toISOString(), confidence: 0.92 },
        { id: "4", type: "progress", agent: "data_quality_agent", message: "Running data quality checks...", timestamp: new Date().toISOString(), confidence: 0.88 },
        { id: "5", type: "success", agent: "viz_agent", message: "Generated 3 charts successfully", timestamp: new Date().toISOString(), confidence: 0.94 },
        { id: "6", type: "complete", agent: "brain_controller", message: "Task completed in 2.3s", timestamp: new Date().toISOString(), duration_ms: 2300 },
      ];

      setIsConnected(true);
      for (const event of mockEvents) {
        await new Promise((r) => setTimeout(r, 500));
        setEvents((prev) => [...prev, event]);
      }
    };

    simulateJob();

    return () => setIsConnected(false);
  }, [taskId, autoConnect]);

  const getIcon = (type: string) => {
    switch (type) {
      case "start": return "🚀";
      case "progress": return "⚡";
      case "success": return "✅";
      case "error": return "❌";
      case "complete": return "🏁";
      default: return "📌";
    }
  };

  const getColor = (type: string) => {
    switch (type) {
      case "start": return "text-blue-400";
      case "progress": return "text-yellow-400";
      case "success": return "text-green-400";
      case "error": return "text-red-400";
      case "complete": return "text-purple-400";
      default: return "text-muted-foreground";
    }
  };

  return (
    <div className="glass-card rounded-lg p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-400 animate-pulse" : "bg-muted-foreground"}`} />
          <h3 className="font-semibold">Brain Theater — Live Execution</h3>
        </div>
        <span className="text-xs text-muted-foreground">{events.length} events</span>
      </div>

      {/* Events Stream */}
      <div className="space-y-2 max-h-96 overflow-y-auto mb-4 p-2 bg-background/50 rounded">
        {events.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <div className="text-4xl mb-2">🧠</div>
            <p>Waiting for tasks...</p>
          </div>
        ) : (
          events.map((event) => (
            <div key={event.id} className="flex items-start gap-3 p-2 rounded hover:bg-accent/50 transition-colors">
              <span className="text-lg">{getIcon(event.type)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-mono ${getColor(event.type)}`}>{event.agent}</span>
                  <span className="text-xs text-muted-foreground">{new Date(event.timestamp).toLocaleTimeString()}</span>
                  {event.confidence !== undefined && (
                    <span className="text-xs px-1.5 py-0.5 rounded bg-primary/10 text-primary">
                      {(event.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                <p className="text-sm mt-0.5">{event.message}</p>
              </div>
            </div>
          ))
        )}
        <div ref={eventsEndRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Enter analysis query..."
          className="flex-1 px-3 py-2 rounded bg-background border border-border text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
        <button className="px-4 py-2 bg-primary text-white rounded hover:bg-primary/90 text-sm font-medium">
          Run
        </button>
      </div>
    </div>
  );
}