import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const serviceKey = process.env.HUBSPOT_PRIVATE_APP_TOKEN;
  const password = process.env.TIKVARON_PREVIEW_PASSWORD;

  if (serviceKey && !password) {
    return new NextResponse("Preview is not secured: configure TIKVARON_PREVIEW_PASSWORD.", { status: 503 });
  }

  if (!password) return NextResponse.next();

  const authorization = request.headers.get("authorization");
  if (authorization?.startsWith("Basic ")) {
    const decoded = atob(authorization.slice(6));
    const suppliedPassword = decoded.slice(decoded.indexOf(":") + 1);
    if (suppliedPassword === password) return NextResponse.next();
  }

  return new NextResponse("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="TIKVARON Sales Growth Preview"' }
  });
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};