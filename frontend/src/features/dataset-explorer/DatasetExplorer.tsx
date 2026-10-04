"use client";

import { useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface Dataset {
  id: string;
  name: string;
  size: string;
  rows: number;
  status: string;
  created: string;
}

export default function DatasetExplorer() {
  const [datasets] = useState<Dataset[]>([
    { id: "1", name: "sales_data_2024.parquet", size: "2.4 GB", rows: 1500000, status: "processed", created: "2024-01-15" },
    { id: "2", name: "customer_feedback.csv", size: "450 MB", rows: 50000, status: "processed", created: "2024-01-14" },
    { id: "3", name: "sensor_readings.json", size: "1.2 GB", rows: 850000, status: "processing", created: "2024-01-13" },
  ]);

  return (
    <div className="glass-card rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Dataset Explorer</h3>
        <button className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90">
          Upload Dataset
        </button>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Size</TableHead>
            <TableHead>Rows</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Created</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {datasets.map(ds => (
            <TableRow key={ds.id}>
              <TableCell className="font-medium">{ds.name}</TableCell>
              <TableCell>{ds.size}</TableCell>
              <TableCell>{ds.rows.toLocaleString()}</TableCell>
              <TableCell>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  ds.status === "processed" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                }`}>
                  {ds.status}
                </span>
              </TableCell>
              <TableCell>{ds.created}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
