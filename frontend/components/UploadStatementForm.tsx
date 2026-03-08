"use client";

import { useState } from "react";
import { api } from "../lib/api";
import { ParseResponse } from "../types/transaction";

type Props = {
  onParsed: (data: ParseResponse) => void;
};

export default function UploadStatementForm({ onParsed }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("No file selected");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      setStatus("Please choose a CSV or PDF file first.");
      return;
    }

    try {
      setLoading(true);
      setStatus("Uploading and parsing statement...");

      const formData = new FormData();
      formData.append("file", file);

      const response = await api.post<ParseResponse>("/upload/statement", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      onParsed(response.data);
      setStatus(`Parsed ${response.data.row_count} transactions successfully.`);
    } catch (error: unknown) {
      const message =
        typeof error === "object" &&
        error !== null &&
          "response" in error &&
        typeof (error as { response?: { data?: { detail?: unknown } } }).response?.data
          ?.detail === "string"
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : "Upload failed. Please check your CSV/PDF.";
      setStatus(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-[22px] border border-white/10 bg-gradient-to-br from-slate-900/90 via-slate-900/75 to-blue-950/60 p-6 shadow-[0_20px_50px_rgba(10,18,40,0.45)]">
      <h2 className="text-xl font-bold text-white">Upload Bank Statement</h2>
      <p className="mt-1 text-sm text-slate-300">
        Upload a PDF statement and generate a full financial intelligence report.
      </p>

      <div className="mt-4 space-y-4">
        <input
          type="file"
          accept=".csv,.pdf,text/csv,application/pdf"
          onChange={(e) => {
            const selected = e.target.files?.[0] || null;
            setFile(selected);
            setStatus(selected ? `Selected: ${selected.name}` : "No file selected");
          }}
          className="block w-full cursor-pointer rounded-xl border border-white/20 bg-white/5 px-3 py-2 text-sm text-slate-200 file:mr-4 file:cursor-pointer file:rounded-lg file:border-0 file:bg-cyan-300/15 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-cyan-100"
        />

        <button
          onClick={handleUpload}
          disabled={loading}
          className="rounded-xl bg-gradient-to-r from-cyan-300 via-blue-300 to-emerald-300 px-4 py-2.5 text-sm font-bold text-slate-900 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Parsing..." : "Upload Statement"}
        </button>

        <p className="text-sm text-slate-300">{status}</p>
      </div>
    </div>
  );
}
