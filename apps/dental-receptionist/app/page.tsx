"use client";

import { FormEvent, useState } from "react";

type Message = { role: "user" | "assistant"; content: string };
type AppointmentRequest = { name: string; contact: string; service: string; date: string; time: string };

const greeting = "Hello! Thank you for getting in touch with the dental clinic. I'm the TIKVARON receptionist demo. How can I help today?";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([{ role: "assistant", content: greeting }]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [request, setRequest] = useState<AppointmentRequest>({ name: "", contact: "", service: "Routine check-up", date: "", time: "" });
  const [preview, setPreview] = useState<AppointmentRequest | null>(null);

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

  function previewRequest(event: FormEvent) {
    event.preventDefault();
    setPreview({ ...request });
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

      <section className="booking" aria-labelledby="booking-title">
        <div className="booking-heading">
          <p className="eyebrow">APPOINTMENT REQUEST</p>
          <h2 id="booking-title">Request a visit</h2>
          <p>Try the appointment form below. This is a preview only; it does not contact a clinic or reserve a time.</p>
        </div>
        <form className="booking-form" onSubmit={previewRequest}>
          <label>Demo name<input value={request.name} onChange={e => { setRequest({ ...request, name: e.target.value }); setPreview(null); }} placeholder="e.g. Alex Demo" required maxLength={80} /></label>
          <label>Demo contact<input value={request.contact} onChange={e => { setRequest({ ...request, contact: e.target.value }); setPreview(null); }} placeholder="Use fictional details only" required maxLength={80} /></label>
          <label>Type of visit<select value={request.service} onChange={e => { setRequest({ ...request, service: e.target.value }); setPreview(null); }}><option>Routine check-up</option><option>Cleaning</option><option>Toothache — staff assessment needed</option><option>Other / not sure</option></select></label>
          <div className="booking-row">
            <label>Preferred date<input type="date" value={request.date} onChange={e => { setRequest({ ...request, date: e.target.value }); setPreview(null); }} required /></label>
            <label>Preferred time<select value={request.time} onChange={e => { setRequest({ ...request, time: e.target.value }); setPreview(null); }} required><option value="">Choose a time</option><option>Morning</option><option>Afternoon</option><option>Any time</option></select></label>
          </div>
          <button className="preview-button" type="submit">Preview appointment request</button>
        </form>
        {preview && <div className="request-preview" role="status">
          <strong>Request preview prepared</strong>
          <p>{preview.name} · {preview.contact}</p>
          <p>{preview.service} · {preview.date} · {preview.time}</p>
          <p className="not-sent">Not sent. No appointment has been booked or reserved.</p>
        </div>}
        <p className="privacy booking-privacy">Use fictional test details only. This form keeps the preview in this page and does not save or transmit it.</p>
      </section>

      <footer>
        <strong>Demo limitations</strong>
        <p>The AI chat needs a valid staging API key. This form is a local preview only: no clinic calendar, phone line, staff handover, or voice connection is connected. It does not save or send appointment requests. Clinical questions must go to a qualified professional.</p>
      </footer>
    </main>
  );
}
