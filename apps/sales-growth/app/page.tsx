"use client";

import { useState } from "react";

type Result = {
  ok?: boolean;
  configured?: boolean;
  connected?: boolean;
  contactFound?: boolean;
  message?: string;
  contact?: {
    id: string;
    email: string;
    firstName: string | null;
    lastName: string | null;
    lifecycleStage: string | null;
    leadStatus: string | null;
  };
};

export default function Home() {
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);

  async function testConnection() {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch("/api/hubspot/test-contact", { cache: "no-store" });
      const data = await response.json();
      setResult(data);
    } catch {
      setResult({ ok: false, message: "Could not reach the application API. Check the Preview deployment." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brandmark">T</div>
        <div><strong>TIKVARON</strong><span>SALES GROWTH</span></div>
        <span className="environment">PRIVATE PREVIEW</span>
      </header>
      <section className="hero">
        <p className="eyebrow">CUSTOMER OPERATIONS / INTEGRATIONS</p>
        <h1>One connected view.<br /><em>Better follow-through.</em></h1>
        <p className="intro">A private workspace for validating TIKVARON's CRM connection before any customer workflow is activated.</p>
      </section>
      <section className="panel">
        <div className="panel-heading">
          <div><p className="eyebrow">INTEGRATION CHECK</p><h2>HubSpot connection</h2></div>
          <span className="dot" />
        </div>
        <p className="panel-copy">This read-only check authenticates with the server-side service key and searches for the approved TIKVARON integration test contact. It does not create, edit, or delete CRM records.</p>
        <button onClick={testConnection} disabled={loading}>{loading ? "Checking HubSpot…" : "Test HubSpot connection"}</button>
        {result && <div className={result.ok && result.connected && result.contactFound ? "result success" : "result"}>
          <strong>{result.ok && result.connected && result.contactFound ? "Connection verified" : "Test result"}</strong>
          <p>{result.message ?? (result.contactFound ? "The integration test contact was found." : "The contact was not found.")}</p>
          {result.contact && <dl>
            <div><dt>Contact</dt><dd>{[result.contact.firstName, result.contact.lastName].filter(Boolean).join(" ") || "—"}</dd></div>
            <div><dt>Email</dt><dd>{result.contact.email}</dd></div>
            <div><dt>Lifecycle</dt><dd>{result.contact.lifecycleStage ?? "—"}</dd></div>
            <div><dt>Lead status</dt><dd>{result.contact.leadStatus ?? "—"}</dd></div>
            <div><dt>HubSpot ID</dt><dd>{result.contact.id}</dd></div>
          </dl>}
        </div>}
      </section>
      <footer>HUMAN-APPROVED OPERATIONS <span>·</span> READ-ONLY VALIDATION <span>·</span> NO CUSTOMER DATA</footer>
    </main>
  );
}