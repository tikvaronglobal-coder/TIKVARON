import { NextRequest, NextResponse } from "next/server";
import { authorizePreview } from "./lib/preview-auth.mjs";

export function middleware(request: NextRequest) {
  const decision = authorizePreview({
    password: process.env.TIKVARON_PREVIEW_PASSWORD ?? "",
    authorization: request.headers.get("authorization"),
    isProduction: process.env.NODE_ENV === "production"
  });

  if (decision === "configuration_error") {
    return new NextResponse("Preview is unavailable until TIKVARON_PREVIEW_PASSWORD is configured.", { status: 503 });
  }

  if (decision === "allow") return NextResponse.next();

  return new NextResponse("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="TIKVARON Sales Growth Preview"' }
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
