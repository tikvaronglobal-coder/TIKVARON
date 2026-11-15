"use client";

import { FormEvent, useState } from "react";

type Message = { role: "user" | "assistant"; content: string };

const greeting = "Hello! Thank you for getting in touch with the dental clinic. I'm the TIKVARON receptionist demo. How can I help today?";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([{ role: "assistant", content: greeting }]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function send(event: FormEvent) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || busy) return;
    const next: Message[] = [...messages, { role: "user", content: text }];
    setMessages(next);
    setDraft("");
    setError("");
    setBusy(true);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: next.slice(-12) })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "The receptionist is unavailable.");
      setMessages([...next, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brandmark">T</div>
        <div><strong>TIKVARON</strong><span>Where Hope Sings.</span></div>
        <span className="status">STAGING DEMO</span>
      </header>
      <section className="intro">
        <p className="eyebrow">DENTAL RECEPTIONIST</p>
        <h1>A more human welcome to dental care.</h1>
        <p>Ask a question, explore an appointment request, or see how the receptionist handles a follow-up.</p>
      </section>
      <section className="chat" aria-label="Receptionist conversation">
        <div className="chathead"><div className="avatar">T</div><div><strong>Dental Receptionist</strong><small>Conversational demo · English</small></div><span className="online">● Demo</span></div>
        <div className="messages" aria-live="polite">
          {messages.map((message, index) => (
            <div className={`message ${message.role}`} key={index}>
              <span>{message.content}</span>
            </div>
          ))}
          {busy && <div className="message assistant"><span>One moment, please…</span></div>}
        </div>
        {error && <p className="error" role="alert">{error}</p>}
        <form className="composer" onSubmit={send}>
          <label className="srOnly" htmlFor="message">Your message</label>
          <input id="message" value={draft} onChange={e => setDraft(e.target.value)} maxLength={2000} placeholder="Type your message…" disabled={busy} />
          <button type="submit" disabled={busy || !draft.trim()}>{busy ? "…" : "Send"}</button>
        </form>
        <p className="privacy">Please don't enter real patient details, symptoms, payment information, or medical records.</p>
      </section>
      <footer>
        <strong>Demo limitations</strong>
        <p>This staging build has no clinic knowledge base, booking calendar, phone line, staff handover, or voice connection. It does not save or send appointment requests. Clinical questions must go to a qualified professional.</p>
      </footer>
    </main>
  );
}