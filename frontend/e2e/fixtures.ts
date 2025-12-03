/* eslint-disable react-hooks/rules-of-hooks */
import { test as base, Page } from "@playwright/test";

// Mock data - Agents
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

// Mock data - Personal Agents
const mockPersonalAgents = [
  {
    id: "33333333-3333-3333-3333-333333333333",
    user_id: "00000000-0000-0000-0000-000000000001",
    name: "My Orchestrator",
    description: "An orchestrator agent for managing tasks",
    system_prompt: "You are an orchestrator agent that manages multiple agents.",
    is_public: false,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  },
];

// Mock data - LLM Configs
const mockLLMConfigs = [
  {
    id: "44444444-4444-4444-4444-444444444444",
    user_id: "00000000-0000-0000-0000-000000000001",
    provider: "openai",
    is_default: true,
    created_at: "2024-01-01T00:00:00Z",
  },
];

// Mock data - API Keys
const mockApiKeys = [
  {
    id: "55555555-5555-5555-5555-555555555555",
    user_id: "00000000-0000-0000-0000-000000000001",
    name: "Production Key",
    key_prefix: "sk_live_abc1...",
    scopes: ["agents:read", "agents:execute"],
    rate_limit: 1000,
    last_used_at: "2024-01-15T10:30:00Z",
    created_at: "2024-01-01T00:00:00Z",
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

  // Mock GET/POST /api/personal-agents
  await page.route("**/api/personal-agents", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mockPersonalAgents),
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

  // Mock GET/PATCH/DELETE /api/personal-agents/:id
  await page.route("**/api/personal-agents/*", async (route) => {
    const url = route.request().url();
    const agentId = url.split("/api/personal-agents/")[1]?.split("?")[0];
    const method = route.request().method();

    if (method === "GET") {
      const agent = mockPersonalAgents.find((a) => a.id === agentId);
      if (agent) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(agent),
        });
      } else {
        await route.fulfill({ status: 404 });
      }
    } else if (method === "PATCH") {
      const agent = mockPersonalAgents.find((a) => a.id === agentId);
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

  // Mock GET/POST /api/user/llm-configs
  await page.route("**/api/user/llm-configs", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mockLLMConfigs),
      });
    } else if (route.request().method() === "POST") {
      const body = route.request().postDataJSON();
      const newConfig = {
        id: crypto.randomUUID(),
        user_id: "00000000-0000-0000-0000-000000000001",
        provider: body.provider,
        is_default: false,
        created_at: new Date().toISOString(),
      };
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify(newConfig),
      });
    } else {
      await route.continue();
    }
  });

  // Mock DELETE /api/user/llm-configs/:id
  await page.route("**/api/user/llm-configs/*", async (route) => {
    if (route.request().method() === "DELETE") {
      await route.fulfill({ status: 204 });
    } else {
      await route.continue();
    }
  });

  // Mock GET/POST /api/user/api-keys
  await page.route("**/api/user/api-keys", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(mockApiKeys),
      });
    } else if (route.request().method() === "POST") {
      const body = route.request().postDataJSON();
      const newKey = {
        id: crypto.randomUUID(),
        user_id: "00000000-0000-0000-0000-000000000001",
        name: body.name,
        key: `sk_live_${crypto.randomUUID().replace(/-/g, "").substring(0, 32)}`,
        key_prefix: "sk_live_xxxx...",
        scopes: body.scopes || [],
        rate_limit: body.rate_limit || 1000,
        last_used_at: null,
        created_at: new Date().toISOString(),
      };
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: JSON.stringify(newKey),
      });
    } else {
      await route.continue();
    }
  });

  // Mock DELETE /api/user/api-keys/:id
  await page.route("**/api/user/api-keys/*", async (route) => {
    if (route.request().method() === "DELETE") {
      await route.fulfill({ status: 204 });
    } else {
      await route.continue();
    }
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
