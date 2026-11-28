import { NextResponse } from "next/server";
import { createHubSpotClient } from "../../../../lib/hubspot.mjs";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const token = process.env.HUBSPOT_PRIVATE_APP_TOKEN;

  if (!token) {
    return NextResponse.json(
      { ok: false, configured: false, message: "HubSpot service key is not configured for this Preview deployment." },
      { status: 503 }
    );
  }

  try {
    const result = await createHubSpotClient({ token }).findIntegrationTestContact();
    return NextResponse.json({ ok: true, configured: true, ...result });
  } catch (error) {
    const message = error instanceof Error ? error.message : "HubSpot connection failed";
    const status = message.includes("status 401") || message.includes("status 403") ? 502 : 502;
    return NextResponse.json(
      { ok: false, configured: true, message },
      { status }
    );
  }
}