export function authorizePreview({ password, authorization, isProduction }) {
  if (!password) {
    return isProduction ? "configuration_error" : "allow";
  }

  if (!authorization?.startsWith("Basic ")) return "challenge";

  try {
    const decoded = atob(authorization.slice(6));
    const separator = decoded.indexOf(":");
    const suppliedPassword = separator >= 0 ? decoded.slice(separator + 1) : "";
    return suppliedPassword === password ? "allow" : "challenge";
  } catch {
    return "challenge";
  }
}
