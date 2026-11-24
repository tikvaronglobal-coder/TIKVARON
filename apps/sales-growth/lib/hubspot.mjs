export const INTEGRATION_TEST_EMAIL = "tikvaron-integration-test@example.com";

export function createHubSpotClient({ token, fetchImpl = fetch }) {
  if (!token || typeof token !== "string") {
    throw new Error("HubSpot service key is not configured");
  }

  return {
    async findIntegrationTestContact() {
      const response = await fetchImpl(
        "https://api.hubapi.com/crm/v3/objects/contacts/search",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            filterGroups: [{
              filters: [{
                propertyName: "email",
                operator: "EQ",
                value: INTEGRATION_TEST_EMAIL
              }]
            }],
            properties: ["email", "firstname", "lastname", "lifecyclestage", "hs_lead_status"],
            limit: 2
          }),
          cache: "no-store"
        }
      );

      if (!response.ok) {
        // Never include upstream response bodies; they may contain sensitive data.
        throw new Error(`HubSpot API request failed with status ${response.status}`);
      }

      const payload = await response.json();
      const results = Array.isArray(payload.results) ? payload.results : [];
      const exactMatches = results.filter(
        (contact) => contact?.properties?.email?.toLowerCase() === INTEGRATION_TEST_EMAIL
      );

      if (exactMatches.length !== 1) {
        return {
          connected: true,
          contactFound: false,
          matchCount: exactMatches.length,
          message: exactMatches.length === 0
            ? "HubSpot authenticated successfully, but the integration test contact was not found."
            : "More than one matching integration test contact was found. Resolve duplicates before continuing."
        };
      }

      const contact = exactMatches[0];
      return {
        connected: true,
        contactFound: true,
        contact: {
          id: String(contact.id),
          email: contact.properties.email,
          firstName: contact.properties.firstname ?? null,
          lastName: contact.properties.lastname ?? null,
          lifecycleStage: contact.properties.lifecyclestage ?? null,
          leadStatus: contact.properties.hs_lead_status ?? null
        }
      };
    }
  };
}