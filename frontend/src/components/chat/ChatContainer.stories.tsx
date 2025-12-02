import type { Meta, StoryObj } from "@storybook/react";
import { ChatContainer } from "./ChatContainer";

const meta: Meta<typeof ChatContainer> = {
  title: "Chat/ChatContainer",
  component: ChatContainer,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof ChatContainer>;

const mockMessages = [
  {
    id: "1",
    role: "user" as const,
    content: "Hi there!",
    timestamp: "10:00 AM",
  },
  {
    id: "2",
    role: "assistant" as const,
    content: "Hello! How can I help you today?",
    timestamp: "10:01 AM",
  },
];

export const Default: Story = {
  args: {
    messages: mockMessages,
  },
};

export const Empty: Story = {
  args: {
    messages: [],
  },
};

export const Loading: Story = {
  args: {
    messages: mockMessages,
    isLoading: true,
  },
};

export const Streaming: Story = {
  args: {
    messages: [
      ...mockMessages,
      {
        id: "3",
        role: "assistant",
        content: "I am thinking...",
      },
    ],
    isStreaming: true,
  },
};
