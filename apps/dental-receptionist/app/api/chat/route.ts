import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

type Message = { role: "user" | "assistant"; content: string };

const SYSTEM_PROMPT = `
You are TIKVARON Dental Receptionist, a warm, calm, professional front-desk assistant.
Speak naturally and conversationally. Answer in clear English. Ask one useful question at a time.
Remember details included in the conversation history and do not ask the caller to repeat them.
You may explain general administrative information, collect appointment preferences, and help
the caller prepare to speak with clinic staff.

Safety and truthfulness:
- This is a staging demo. No real clinic facts, address, phone, prices, insurance, staff,
  opening hours, appointment availability, or booking integration have been configured.
- Never invent clinic-specific facts or claim an appointment is booked, changed, or cancelled.
  You may say you can record a request for staff follow-up, but this demo does not send it.
- Do not diagnose, prescribe, recommend medication, or interpret symptoms or images.
  Refer clinical questions to a qualified dental professional.
- If the caller describes facial/throat swelling, difficulty breathing or swallowing,
  uncontrolled bleeding, major facial trauma, or another immediately dangerous symptom,
  advise seeking urgent in-person medical/dental care now or contacting local emergency
  services. Do not delay urgent care to continue chatting.
- For pain, infection concerns, pregnancy, medication, children, safeguarding, complaints,
  privacy requests, or uncertainty, offer human staff follow-up rather than clinical advice.
- Do not ask for or repeat sensitive medical details, identity numbers, payment details,
  passwords, or full patient records. Ask callers not to share them here.
- If you cannot answer from the configured information, say so plainly and offer staff follow-up.
- Do not claim a human has been contacted. No staff handover channel is connected.
`.trim();

function extractText(data: any): string {
  if (typeof data?.output_text === "string" && data.output_text.trim()) {
    return data.output_text.trim();
  }
  const parts: string[] = [];
  for (const item of data?.output ?? []) {
    for (const content of item?.content ?? []) {
      if (content?.type === "output_text" && typeof content.text === "string") {
        parts.push(content.text);
      } else if (content?.type === "refusal" && typeof content.refusal === "string") {
        parts.push(content.refusal);
      }
    }
  }
  return parts.join("\n").trim();
}

export async function POST(request: NextRequest) {
  const apiKey = process.env.OPENAI_API_KEY;
  const model = process.env.OPENAI_MODEL;

  if (!apiKey || !model) {
    return NextResponse.json(
      { error: "Staging AI is not configured. Check OPENAI_API_KEY and OPENAI_MODEL in the Vercel Preview environment." },
      { status: 503 }
    );
  }

  let body: { messages?: Message[] };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const messages = Array.isArray(body.messages) ? body.messages : [];
  if (messages.length === 0 || messages.length > 20) {
    return NextResponse.json({ error: "Send between 1 and 20 recent messages." }, { status: 400 });
  }

  const safeMessages: Message[] = [];
  for (const message of messages) {
    if (!message || !["user", "assistant"].includes(message.role) || typeof message.content !== "string") {
      return NextResponse.json({ error: "Invalid message format." }, { status: 400 });
    }
    const content = message.content.trim();
    if (!content || content.length > 2000) {
      return NextResponse.json({ error: "Each message must be 1–2000 characters." }, { status: 400 });
    }
    safeMessages.push({ role: message.role, content });
  }

  try {
    const upstream = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model,
        instructions: SYSTEM_PROMPT,
        input: safeMessages.map(({ role, content }) => ({ role, content })),
        max_output_tokens: 350,
        store: false
      }),
      cache: "no-store"
    });

    let data: any = {};
    try {
      data = await upstream.json();
    } catch {
      // The upstream response was not valid JSON; keep the public error generic.
    }

    if (!upstream.ok) {
      const upstreamCode = typeof data?.error?.code === "string" ? data.error.code : "unknown";
      console.error("OpenAI Responses API rejected staging request", {
        status: upstream.status,
        code: upstreamCode,
        modelConfigured: Boolean(model)
      });

      if (upstream.status === 401) {
        return NextResponse.json(
          { error: "The staging OpenAI API key was rejected (401). Replace OPENAI_API_KEY with a valid key from the TIKVARON-Dental-Staging project in Vercel → Preview, then redeploy." },
          { status: 503 }
        );
      }
      if (upstream.status === 429) {
        return NextResponse.json(
          { error: "The staging AI account has reached a rate or usage limit. Check API billing, project limits, and usage before trying again." },
          { status: 503 }
        );
      }
      if (upstream.status === 400) {
        return NextResponse.json(
          { error: "The staging AI request was rejected. Check that OPENAI_MODEL is an available model for this API project." },
          { status: 503 }
        );
      }
      return NextResponse.json(
        { error: "The AI provider could not complete the staging request. Check the Vercel runtime logs for the upstream status." },
        { status: 502 }
      );
    }

    const reply = extractText(data);
    if (!reply) {
      console.error("OpenAI Responses API returned no extractable text", { status: upstream.status });
      return NextResponse.json({ error: "The assistant returned an empty response. Please try again." }, { status: 502 });
    }
    return NextResponse.json({ reply });
  } catch (error) {
    console.error("Staging AI network request failed", error instanceof Error ? error.name : "unknown");
    return NextResponse.json({ error: "Could not reach the AI provider. Please check the staging deployment and try again." }, { status: 502 });
  }
}
