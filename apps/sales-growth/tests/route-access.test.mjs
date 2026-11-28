import test from "node:test";
import assert from "node:assert/strict";
import { isProtectedPath } from "../lib/route-access.mjs";

test("public editorial pages remain outside the private operations gate", () => {
  for (const path of ["/", "/about", "/contact", "/privacy", "/affiliate-disclosure", "/articles/follow-up-problems", "/articles/business-software-guide"]) {
    assert.equal(isProtectedPath(path), false, path);
  }
});

test("internal tools and API routes remain protected", () => {
  for (const path of ["/internal", "/internal/hubspot", "/api/hubspot/test-contact", "/api/anything"]) {
    assert.equal(isProtectedPath(path), true, path);
  }
});
