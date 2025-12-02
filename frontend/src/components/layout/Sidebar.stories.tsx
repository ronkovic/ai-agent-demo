import type { Meta, StoryObj } from "@storybook/react";
import { Sidebar } from "./Sidebar";
import { AgentResponse } from "@/lib/api-client/types.gen";

const meta: Meta<typeof Sidebar> = {
  title: "Layout/Sidebar",
  component: Sidebar,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof Sidebar>;

const mockAgents: AgentResponse[] = [
  {
    id: "1",
    name: "Coding Assistant",
    description: "Helps with coding",
    system_prompt: "You are a coding assistant",
    llm_provider: "claude",
    llm_model: "claude-3-5-sonnet-20241022",
    tools: [],
    a2a_enabled: false,
    user_id: "user1",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "2",
    name: "Writing Helper",
    description: "Helps with writing",
    system_prompt: "You are a writing assistant",
    llm_provider: "openai",
    llm_model: "gpt-4o",
    tools: [],
    a2a_enabled: false,
    user_id: "user1",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: "3",
    name: "Data Analyst",
    description: "Helps with data",
    system_prompt: "You are a data analyst",
    llm_provider: "bedrock",
    llm_model: "anthropic.claude-3-haiku-20240307-v1:0",
    tools: [],
    a2a_enabled: false,
    user_id: "user1",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

export const Default: Story = {
  args: {
    agents: mockAgents,
    selectedAgentId: "1",
  },
};

export const Empty: Story = {
  args: {
    agents: [],
  },
};

export const Selected: Story = {
  args: {
    agents: mockAgents,
    selectedAgentId: "2",
  },
};
