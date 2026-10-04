"use client";

import { useEffect, useRef } from "react";

interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
  language?: string;
  readOnly?: boolean;
  height?: string;
  theme?: "vs-dark" | "vs-light";
}

export default function MonacoEditor({
  value,
  onChange,
  language = "sql",
  readOnly = false,
  height = "400px",
  theme = "vs-dark",
}: MonacoEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<any>(null);

  useEffect(() => {
    // Simulate Monaco editor with textarea for demo
    const container = containerRef.current;
    if (!container) return;

    const textarea = document.createElement("textarea");
    textarea.className = "monaco-editor-mock w-full h-full bg-[#1e1e1e] text-[#d4d4d4] font-mono text-sm p-4 resize-none outline-none border-none";
    textarea.value = value;
    textarea.style.height = height;
    textarea.style.color = "#d4d4d4";
    textarea.style.backgroundColor = "#1e1e1e";

    if (readOnly) {
      textarea.readOnly = true;
      textarea.style.cursor = "default";
    }

    container.innerHTML = "";
    container.appendChild(textarea);

    textarea.addEventListener("input", (e) => {
      onChange(e.currentTarget.value);
    });

    editorRef.current = textarea;

    return () => {
      if (container.children[0]) {
        container.children[0].remove();
      }
    };
  }, [height, language, onChange, readOnly, theme, value]);

  return (
    <div
      ref={containerRef}
      className="rounded border border-border overflow-hidden"
      style={{ height }}
    />
  );
}