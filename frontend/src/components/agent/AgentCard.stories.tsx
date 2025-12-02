import type { Meta, StoryObj } from "@storybook/react";
import { AgentCard } from "./AgentCard";
import { AgentResponse } from "@/lib/api-client/types.gen";

const meta: Meta<typeof AgentCard> = {
  title: "Agent/AgentCard",
  component: AgentCard,
  parameters: {
    layout: "padded",
  },
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof AgentCard>;

const mockAgent: AgentResponse = {
  id: "1",
  name: "Coding Assistant",
  description: "A helpful assistant for writing code and debugging issues.",
  system_prompt: "You are a coding assistant.",
  llm_provider: "claude",
  llm_model: "claude-3-5-sonnet-20241022",
  tools: [],
  a2a_enabled: false,
  user_id: "user1",
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

export const Default: Story = {
  args: {
    agent: mockAgent,
  },
};

export const NoDescription: Story = {
  args: {
    agent: {
      ...mockAgent,
      description: null,
    },
  },
};

export const OpenAI: Story = {
  args: {
    agent: {
      ...mockAgent,
      name: "GPT-4 Helper",
      llm_provider: "openai",
      llm_model: "gpt-4o",
    },
  },
};
