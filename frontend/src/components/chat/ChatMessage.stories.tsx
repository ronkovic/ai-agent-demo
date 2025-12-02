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

// Tool call stories
export const WithToolExecuting: Story = {
  args: {
    role: "assistant",
    content: "Executing code...",
    timestamp: "12:03 PM",
    toolCalls: [
      {
        id: "call_1",
        name: "execute_code",
        arguments: {
          language: "python",
          code: 'print("Hello from Python!")',
        },
      },
    ],
    isToolExecuting: true,
  },
};

export const WithToolSuccess: Story = {
  args: {
    role: "assistant",
    content: "Code executed successfully",
    timestamp: "12:04 PM",
    toolCalls: [
      {
        id: "call_1",
        name: "execute_code",
        arguments: {
          language: "python",
          code: 'for i in range(3):\n    print(f"Count: {i}")',
        },
      },
    ],
    toolResult: {
      toolCallId: "call_1",
      success: true,
      output: "Count: 0\nCount: 1\nCount: 2",
    },
    isToolExecuting: false,
  },
};

export const WithToolError: Story = {
  args: {
    role: "assistant",
    content: "Code execution failed",
    timestamp: "12:05 PM",
    toolCalls: [
      {
        id: "call_2",
        name: "execute_code",
        arguments: {
          language: "python",
          code: "import nonexistent_module",
        },
      },
    ],
    toolResult: {
      toolCallId: "call_2",
      success: false,
      output: null,
      error: "ModuleNotFoundError: No module named 'nonexistent_module'",
    },
    isToolExecuting: false,
  },
};

export const WithWebSearch: Story = {
  args: {
    role: "assistant",
    content: "Searching the web...",
    timestamp: "12:06 PM",
    toolCalls: [
      {
        id: "call_3",
        name: "web_search",
        arguments: {
          query: "React best practices 2024",
          max_results: 5,
        },
      },
    ],
    toolResult: {
      toolCallId: "call_3",
      success: true,
      output: [
        {
          title: "React Best Practices",
          url: "https://example.com/react",
          snippet: "Learn modern React patterns...",
        },
      ],
    },
    isToolExecuting: false,
  },
};
