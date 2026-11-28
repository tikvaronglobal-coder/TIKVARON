const PRIVATE_PREFIXES = ["/internal", "/api"];

export function isProtectedPath(pathname) {
  return PRIVATE_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(prefix + "/"));
}
