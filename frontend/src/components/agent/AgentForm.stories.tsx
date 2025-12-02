import type { Meta, StoryObj } from "@storybook/react";
import { AgentForm } from "./AgentForm";

const meta: Meta<typeof AgentForm> = {
  title: "Agent/AgentForm",
  component: AgentForm,
  parameters: {
    layout: "padded",
  },
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof AgentForm>;

export const Create: Story = {
  args: {
    onSubmit: (data) => console.log(data),
    onCancel: () => console.log("Cancelled"),
  },
};

export const Edit: Story = {
  args: {
    initialData: {
      name: "Existing Agent",
      description: "An existing agent description",
      system_prompt: "You are an existing agent.",
      llm_provider: "openai",
      llm_model: "gpt-4o",
    },
    onSubmit: (data) => console.log(data),
    onCancel: () => console.log("Cancelled"),
  },
};

export const Loading: Story = {
  args: {
    isLoading: true,
    onSubmit: (data) => console.log(data),
    onCancel: () => console.log("Cancelled"),
  },
};
