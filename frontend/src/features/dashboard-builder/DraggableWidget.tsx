"use client";

import { useRef, useState } from "react";

interface WidgetProps {
  id: string;
  type: "chart" | "table" | "kpi" | "text";
  title: string;
  position: { x: number; y: number; w: number; h: number };
  onDelete?: (id: string) => void;
  onEdit?: (id: string, updates: Partial<WidgetProps>) => void;
}

export default function DraggableWidget({ id, type, title, position, onDelete, onEdit }: WidgetProps) {
  const [isDragging, setIsDragging] = useState(false);
  const dragRef = useRef<{ startX: number; startY: number; origX: number; origY: number } | null>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    dragRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      origX: position.x,
      origY: position.y,
    };
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging || !dragRef.current) return;
    const dx = e.clientX - dragRef.current.startX;
    const dy = e.clientY - dragRef.current.startY;
    onEdit?.(id, {
      position: {
        ...position,
        x: Math.max(0, dragRef.current.origX + Math.round(dx / 80)),
        y: Math.max(0, dragRef.current.origY + Math.round(dy / 60)),
      },
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    dragRef.current = null;
  };

  useState(() => {
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  });

  const widgetContent = () => {
    switch (type) {
      case "chart":
        return <div className="h-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded flex items-center justify-center text-sm text-muted-foreground">📊 Chart Preview</div>;
      case "table":
        return <div className="h-full bg-gradient-to-br from-green-500/20 to-teal-500/20 rounded flex items-center justify-center text-sm text-muted-foreground">📋 Table Preview</div>;
      case "kpi":
        return <div className="h-full bg-gradient-to-br from-orange-500/20 to-red-500/20 rounded flex items-center justify-center text-2xl font-bold text-primary">1,234</div>;
      case "text":
        return <div className="h-full bg-gradient-to-br from-gray-500/20 to-slate-500/20 rounded flex items-center justify-center text-sm text-muted-foreground">📝 Text Block</div>;
    }
  };

  return (
    <div
      className={`absolute border border-border rounded-lg bg-card shadow-sm transition-shadow hover:shadow-md ${isDragging ? "shadow-lg cursor-grabbing z-50" : "cursor-move"}`}
      style={{
        left: `${position.x * 8.33}%`,
        top: `${position.y * 4}%`,
        width: `${position.w * 8.33}%`,
        height: `${position.h * 12}rem`,
      }}
      onMouseDown={handleMouseDown}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border bg-muted/30 rounded-t-lg">
        <span className="text-sm font-medium truncate">{title}</span>
        <div className="flex gap-1">
          <button
            onClick={(e) => { e.stopPropagation(); onEdit?.(id, { title: `${title} (copy)` }); }}
            className="p-1 hover:bg-accent rounded text-muted-foreground hover:text-foreground"
            title="Duplicate"
          >
            ⧉
          </button>
          {onDelete && (
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(id); }}
              className="p-1 hover:bg-destructive/10 rounded text-muted-foreground hover:text-destructive"
              title="Delete"
            >
              ×
            </button>
          )}
        </div>
      </div>
      {/* Content */}
      <div className="p-3 h-[calc(100%-2.5rem)]">
        {widgetContent()}
      </div>
    </div>
  );
}