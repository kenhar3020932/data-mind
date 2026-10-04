"use client";

import { useState, useEffect } from "react";
import { Brain, Cpu, Zap, CheckCircle, AlertCircle } from "lucide-react";

interface BrainEvent {
  stage: string;
  action: string;
  timestamp: string;
  confidence?: number;
}

export default function BrainTheater() {
  const [events, setEvents] = useState<BrainEvent[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    // Simulate brain events for demo
    const stages = ["understand", "profile", "plan", "critique", "execute", "verify", "learn"];
    let index = 0;

    const interval = setInterval(() => {
      if (index < stages.length) {
        setEvents(prev => [...prev, {
          stage: stages[index],
          action: `Processing ${stages[index]}...`,
          timestamp: new Date().toISOString(),
          confidence: 0.85 + Math.random() * 0.15,
        }]);
        index++;
      } else {
        setIsProcessing(false);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  const getStageIcon = (stage: string) => {
    const icons: Record<string, typeof Brain> = {
      understand: Brain,
      profile: Cpu,
      plan: Zap,
      critique: AlertCircle,
      execute: CheckCircle,
      verify: CheckCircle,
      learn: Brain,
    };
    return icons[stage] || Brain;
  };

  const getStageColor = (stage: string) => {
    const colors: Record<string, string> = {
      understand: "bg-blue-500",
      profile: "bg-green-500",
      plan: "bg-yellow-500",
      critique: "bg-orange-500",
      execute: "bg-purple-500",
      verify: "bg-teal-500",
      learn: "bg-pink-500",
    };
    return colors[stage] || "bg-gray-500";
  };

  return (
    <div className="glass-card rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Brain className="w-5 h-5 text-primary" />
          Brain Theater
        </h3>
        <span className={`text-sm ${isProcessing ? 'text-green-500' : 'text-gray-500'}`}>
          {isProcessing ? "Processing..." : "Idle"}
        </span>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {events.length === 0 ? (
          <p className="text-muted-foreground text-center py-8">
            Start a task to see the Brain Theater in action
          </p>
        ) : (
          events.map((event, idx) => {
            const Icon = getStageIcon(event.stage);
            return (
              <div
                key={idx}
                className="flex items-center gap-3 p-3 rounded-md bg-background/50 animate-fade-in"
              >
                <div className={`w-2 h-2 rounded-full ${getStageColor(event.stage)}`} />
                <Icon className="w-4 h-4 text-muted-foreground" />
                <div className="flex-1">
                  <span className="font-medium capitalize">{event.stage}</span>
                  <span className="text-muted-foreground ml-2">{event.action}</span>
                </div>
                {event.confidence && (
                  <span className="text-xs text-muted-foreground">
                    {(event.confidence * 100).toFixed(0)}%
                  </span>
                )}
                <span className="text-xs text-muted-foreground">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
