export const INTEGRATION_TEST_EMAIL: string;
export function createHubSpotClient(options: {
  token: string;
  fetchImpl?: typeof fetch;
}): {
  findIntegrationTestContact(): Promise<{
    connected: boolean;
    contactFound: boolean;
    matchCount?: number;
    message?: string;
    contact?: {
      id: string;
      email: string;
      firstName: string | null;
      lastName: string | null;
      lifecycleStage: string | null;
      leadStatus: string | null;
    };
  }>;
};