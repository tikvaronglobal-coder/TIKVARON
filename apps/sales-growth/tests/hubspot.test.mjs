import test from "node:test";
import assert from "node:assert/strict";
import { createHubSpotClient, INTEGRATION_TEST_EMAIL } from "../lib/hubspot.mjs";

test("searches only for the known TIKVARON integration contact", async () => {
  let request;
  const client = createHubSpotClient({
    token: "test-secret",
    fetchImpl: async (url, options) => {
      request = { url, options };
      return {
        ok: true,
        json: async () => ({
          results: [{
            id: "test-contact-id",
            properties: {
              email: INTEGRATION_TEST_EMAIL,
              firstname: "TIKVARON",
              lastname: "Integration Test",
              lifecyclestage: "lead",
              hs_lead_status: "NEW"
            }
          }]
        })
      };
    }
  });

  const result = await client.findIntegrationTestContact();
  assert.equal(request.url, "https://api.hubapi.com/crm/v3/objects/contacts/search");
  assert.equal(request.options.headers.Authorization, "Bearer test-secret");
  const body = JSON.parse(request.options.body);
  assert.equal(body.filterGroups[0].filters[0].value, INTEGRATION_TEST_EMAIL);
  assert.deepEqual(result.contact, {
    id: "test-contact-id",
    email: INTEGRATION_TEST_EMAIL,
    firstName: "TIKVARON",
    lastName: "Integration Test",
    lifecycleStage: "lead",
    leadStatus: "NEW"
  });
});

test("does not return a contact when HubSpot finds no exact email match", async () => {
  const client = createHubSpotClient({
    token: "test-secret",
    fetchImpl: async () => ({ ok: true, json: async () => ({ results: [] }) })
  });
  const result = await client.findIntegrationTestContact();
  assert.equal(result.connected, true);
  assert.equal(result.contactFound, false);
});

test("does not leak upstream error bodies", async () => {
  const client = createHubSpotClient({
    token: "test-secret",
    fetchImpl: async () => ({
      ok: false,
      status: 401,
      text: async () => "sensitive upstream response"
    })
  });
  await assert.rejects(
    () => client.findIntegrationTestContact(),
    (error) => error.message === "HubSpot API request failed with status 401"
  );
});

test("rejects missing service key before making a request", () => {
  assert.throws(() => createHubSpotClient({ token: "" }), /not configured/);
});