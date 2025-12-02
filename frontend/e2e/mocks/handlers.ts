import { http, HttpResponse } from "msw";

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

// Use relative paths for browser interception (works with Next.js rewrites)
// MSW intercepts at browser level before requests go to Next.js server

export const handlers = [
  // List agents
  http.get("*/api/agents", () => {
    return HttpResponse.json(mockAgents);
  }),

  // Get single agent
  http.get("*/api/agents/:agentId", ({ params }) => {
    const agent = mockAgents.find((a) => a.id === params.agentId);
    if (!agent) {
      return new HttpResponse(null, { status: 404 });
    }
    return HttpResponse.json(agent);
  }),

  // Create agent
  http.post("*/api/agents", async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>;
    const newAgent = {
      id: crypto.randomUUID(),
      user_id: "00000000-0000-0000-0000-000000000001",
      ...body,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    mockAgents.push(newAgent as (typeof mockAgents)[0]);
    return HttpResponse.json(newAgent, { status: 201 });
  }),

  // Update agent
  http.put("*/api/agents/:agentId", async ({ params, request }) => {
    const agentIndex = mockAgents.findIndex((a) => a.id === params.agentId);
    if (agentIndex === -1) {
      return new HttpResponse(null, { status: 404 });
    }
    const body = (await request.json()) as Record<string, unknown>;
    mockAgents[agentIndex] = {
      ...mockAgents[agentIndex],
      ...body,
      updated_at: new Date().toISOString(),
    };
    return HttpResponse.json(mockAgents[agentIndex]);
  }),

  // Delete agent
  http.delete("*/api/agents/:agentId", ({ params }) => {
    const agentIndex = mockAgents.findIndex((a) => a.id === params.agentId);
    if (agentIndex === -1) {
      return new HttpResponse(null, { status: 404 });
    }
    mockAgents.splice(agentIndex, 1);
    return new HttpResponse(null, { status: 204 });
  }),

  // Chat endpoint (SSE streaming mock)
  http.post("*/api/chat/stream", async ({ request }) => {
    const body = (await request.json()) as { message?: string };
    const userMessage = body?.message || "Hello";

    // Create SSE response
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        // Send mock streaming response
        const events = [
          { type: "start", data: {} },
          {
            type: "content",
            data: { content: `I received your message: "${userMessage}". ` },
          },
          {
            type: "content",
            data: { content: "How can I help you today?" },
          },
          { type: "end", data: {} },
        ];

        events.forEach((event, index) => {
          setTimeout(() => {
            const data = `event: ${event.type}\ndata: ${JSON.stringify(event.data)}\n\n`;
            controller.enqueue(encoder.encode(data));
            if (index === events.length - 1) {
              controller.close();
            }
          }, index * 100);
        });
      },
    });

    return new HttpResponse(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  }),

  // Health check
  http.get("*/health", () => {
    return HttpResponse.json({ status: "healthy" });
  }),
];
