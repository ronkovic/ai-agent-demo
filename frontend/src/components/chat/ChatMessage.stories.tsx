import type { Meta, StoryObj } from "@storybook/react";
import { ChatMessage } from "./ChatMessage";

const meta: Meta<typeof ChatMessage> = {
  title: "Chat/ChatMessage",
  component: ChatMessage,
  parameters: {
    layout: "padded",
  },
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof ChatMessage>;

export const UserMessage: Story = {
  args: {
    role: "user",
    content: "Hello, how are you?",
    timestamp: "12:00 PM",
  },
};

export const AssistantMessage: Story = {
  args: {
    role: "assistant",
    content: "I am doing well, thank you! How can I help you today?",
    timestamp: "12:01 PM",
  },
};

export const WithCode: Story = {
  args: {
    role: "assistant",
    content: "Here is a simple python function:\n\n```python\ndef hello():\n    print('Hello World')\n```",
    timestamp: "12:02 PM",
  },
};

export const Streaming: Story = {
  args: {
    role: "assistant",
    content: "Thinking about your request...",
    isStreaming: true,
  },
};
