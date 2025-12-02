/* eslint-disable react-hooks/rules-of-hooks */
import { test as base, Page } from "@playwright/test";

// Mock data
const mockAgents = [
  {
    id: "11111111-1111-1111-1111-111111111111",
    user_id: "00000000-0000-0000-0000-000000000001",
    name: "Code Assistant",
    description: "A helpful coding assistant",
    system_prompt: "You are a helpful coding assistant.",
    llm_provider: "claude",
    llm_model: "claude-3-5-sonnet-20241022",
    tools: ["code_execution"],
    a2a_enabled: false,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
  {
    id: "22222222-2222-2222-2222-222222222222",
    user_id: "00000000-0000-0000-0000-000000000001",
    name: "Research Agent",
    description: "An agent for research tasks",
    system_prompt: "You are a research assistant.",
    llm_provider: "claude",
    llm_model: "claude-3-5-sonnet-20241022",
    tools: ["web_search"],
    a2a_enabled: true,
    created_at: "2024-01-02T00:00:00Z",
    updated_at: "2024-01-02T00:00:00Z",
  },
];

/**
 * Set up API mocking for a page
 */
async function setupApiMocks(page: Page) {
  // Mock GET /api/agents
  await page.route("**/api/agents", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mockAgents),
      });
    } else if (route.request().method() === "POST") {
      const body = route.request().postDataJSON();
      const newAgent = {
        id: crypto.randomUUID(),
        user_id: "00000000-0000-0000-0000-000000000001",
        ...body,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify(newAgent),
      });
    } else {
      await route.continue();
    }
  });

  // Mock GET/PUT/DELETE /api/agents/:id
  await page.route("**/api/agents/*", async (route) => {
    const url = route.request().url();
    const agentId = url.split("/api/agents/")[1]?.split("?")[0];
    const method = route.request().method();

    if (method === "GET") {
      const agent = mockAgents.find((a) => a.id === agentId);
      if (agent) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(agent),
        });
      } else {
        await route.fulfill({ status: 404 });
      }
    } else if (method === "PUT" || method === "PATCH") {
      const agent = mockAgents.find((a) => a.id === agentId);
      if (agent) {
        const body = route.request().postDataJSON();
        const updated = { ...agent, ...body, updated_at: new Date().toISOString() };
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(updated),
        });
      } else {
        await route.fulfill({ status: 404 });
      }
    } else if (method === "DELETE") {
      await route.fulfill({ status: 204 });
    } else {
      await route.continue();
    }
  });

  // Mock POST /api/chat/stream (SSE)
  await page.route("**/api/chat/stream", async (route) => {
    const body = route.request().postDataJSON();
    const userMessage = body?.message || "Hello";

    const events = [
      `event: start\ndata: {}\n\n`,
      `event: content\ndata: {"content":"I received your message: \\"${userMessage}\\". "}\n\n`,
      `event: content\ndata: {"content":"How can I help you today?"}\n\n`,
      `event: end\ndata: {}\n\n`,
    ].join("");

    await route.fulfill({
      status: 200,
      contentType: "text/event-stream",
      headers: {
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
      body: events,
    });
  });

  // Mock health check
  await page.route("**/health", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ status: "healthy" }),
    });
  });
}

// Extended test with API mocking
export const test = base.extend({
  page: async ({ page }, use) => {
    await setupApiMocks(page);
    await use(page);
  },
});

export { expect } from "@playwright/test";
