"use client";

import { useState } from "react";

export default function DashboardBuilder() {
  const [widgets, setWidgets] = useState([
    { id: "1", type: "chart", title: "Sales Overview", position: { x: 0, y: 0, w: 6, h: 4 } },
    { id: "2", type: "table", title: "Recent Orders", position: { x: 6, y: 0, w: 6, h: 4 } },
    { id: "3", type: "kpi", title: "Total Revenue", position: { x: 0, y: 4, w: 4, h: 2 } },
    { id: "4", type: "kpi", title: "Customers", position: { x: 4, y: 4, w: 4, h: 2 } },
    { id: "5", type: "kpi", title: "Growth", position: { x: 8, y: 4, w: 4, h: 2 } },
  ]);

  return (
    <div className="glass-card rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Dashboard Builder</h3>
        <button className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90">
          Add Widget
        </button>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {widgets.map(widget => (
          <div
            key={widget.id}
            className={`p-4 bg-background/50 border rounded-md ${
              widget.position.w === 6 ? "col-span-6" :
              widget.position.w === 4 ? "col-span-4" : "col-span-3"
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">{widget.title}</span>
              <button className="text-muted-foreground hover:text-foreground">✕</button>
            </div>
            <div className="h-24 bg-accent/10 rounded flex items-center justify-center">
              <span className="text-sm text-muted-foreground">
                {widget.type === "chart" ? "Chart" :
                 widget.type === "table" ? "Table" :
                 "KPI: 1,234"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
