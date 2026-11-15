import { NextRequest, NextResponse } from "next/server";

/**
 * Protect billable staging deployments with HTTP Basic Auth.
 * Set TIKVARON_PREVIEW_PASSWORD in the deployment environment before adding
 * OPENAI_API_KEY. The route fails closed (503) if a billable key is present
 * without the password being configured.
 */
export function middleware(request: NextRequest) {
  // No billable API key: the static/demo UI can be browsed without credentials.
  if (!process.env.OPENAI_API_KEY) {
    return NextResponse.next();
  }

  const expectedPassword = process.env.TIKVARON_PREVIEW_PASSWORD;
  if (!expectedPassword) {
    return new NextResponse("Staging access protection is not configured. Contact the project administrator.", {
      status: 503,
      headers: { "Cache-Control": "no-store" }
    });
  }

  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Basic ")) {
    return new NextResponse("Authentication required.", {
      status: 401,
      headers: {
        "WWW-Authenticate": 'Basic realm="TIKVARON Dental Staging", charset="UTF-8"',
        "Cache-Control": "no-store"
      }
    });
  }

  try {
    const credentials = atob(authorization.slice(6));
    const separator = credentials.indexOf(":");
    const suppliedPassword = separator >= 0 ? credentials.slice(separator + 1) : "";
    if (suppliedPassword !== expectedPassword) {
      return new NextResponse("Invalid staging credentials.", {
        status: 401,
        headers: {
          "WWW-Authenticate": 'Basic realm="TIKVARON Dental Staging", charset="UTF-8"',
          "Cache-Control": "no-store"
        }
      });
    }
  } catch {
    return new NextResponse("Invalid authorization header.", {
      status: 401,
      headers: {
        "WWW-Authenticate": 'Basic realm="TIKVARON Dental Staging", charset="UTF-8"',
        "Cache-Control": "no-store"
      }
    });
  }

  const response = NextResponse.next();
  response.headers.set("Cache-Control", "no-store");
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
