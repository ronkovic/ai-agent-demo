import type { Meta, StoryObj } from "@storybook/react";
import { ToolCallDisplay, ToolCallBadge } from "./ToolCall";

const meta: Meta<typeof ToolCallDisplay> = {
  title: "Chat/ToolCall",
  component: ToolCallDisplay,
  parameters: {
    layout: "padded",
  },
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof ToolCallDisplay>;

// ToolCallDisplay Stories
export const CodeExecutionPending: Story = {
  args: {
    toolCall: {
      id: "call_1",
      name: "execute_code",
      arguments: {
        language: "python",
        code: 'print("Hello, World!")',
      },
    },
    isExecuting: true,
  },
};

export const CodeExecutionSuccess: Story = {
  args: {
    toolCall: {
      id: "call_1",
      name: "execute_code",
      arguments: {
        language: "python",
        code: 'for i in range(5):\n    print(f"Number: {i}")',
      },
    },
    result: {
      toolCallId: "call_1",
      success: true,
      output: "Number: 0\nNumber: 1\nNumber: 2\nNumber: 3\nNumber: 4",
    },
    isExecuting: false,
  },
};

export const CodeExecutionError: Story = {
  args: {
    toolCall: {
      id: "call_2",
      name: "execute_code",
      arguments: {
        language: "python",
        code: "print(undefined_variable)",
      },
    },
    result: {
      toolCallId: "call_2",
      success: false,
      output: null,
      error: "NameError: name 'undefined_variable' is not defined",
    },
    isExecuting: false,
  },
};

export const WebSearchPending: Story = {
  args: {
    toolCall: {
      id: "call_3",
      name: "web_search",
      arguments: {
        query: "latest AI news 2024",
        max_results: 5,
      },
    },
    isExecuting: true,
  },
};

export const WebSearchSuccess: Story = {
  args: {
    toolCall: {
      id: "call_3",
      name: "web_search",
      arguments: {
        query: "TypeScript best practices",
        max_results: 3,
      },
    },
    result: {
      toolCallId: "call_3",
      success: true,
      output: [
        {
          title: "TypeScript Best Practices 2024",
          url: "https://example.com/typescript-best-practices",
          snippet:
            "Learn the most effective TypeScript patterns and practices for modern development...",
        },
        {
          title: "Official TypeScript Handbook",
          url: "https://www.typescriptlang.org/docs/handbook/",
          snippet:
            "The TypeScript Handbook is a comprehensive guide to the TypeScript language...",
        },
      ],
    },
    isExecuting: false,
  },
};

export const UnknownTool: Story = {
  args: {
    toolCall: {
      id: "call_4",
      name: "custom_tool",
      arguments: {
        param1: "value1",
        nested: {
          key: "value",
        },
      },
    },
    isExecuting: false,
  },
};

// ToolCallBadge Stories
export const BadgeDefault: StoryObj<typeof ToolCallBadge> = {
  render: () => (
    <ToolCallBadge
      toolCall={{
        id: "call_1",
        name: "execute_code",
        arguments: { language: "python", code: "print(1)" },
      }}
    />
  ),
};

export const BadgeExecuting: StoryObj<typeof ToolCallBadge> = {
  render: () => (
    <ToolCallBadge
      toolCall={{
        id: "call_1",
        name: "web_search",
        arguments: { query: "test" },
      }}
      isExecuting={true}
    />
  ),
};

export const BadgeSuccess: StoryObj<typeof ToolCallBadge> = {
  render: () => (
    <ToolCallBadge
      toolCall={{
        id: "call_1",
        name: "execute_code",
        arguments: { language: "python", code: "print(1)" },
      }}
      result={{
        toolCallId: "call_1",
        success: true,
        output: "1",
      }}
    />
  ),
};

export const BadgeError: StoryObj<typeof ToolCallBadge> = {
  render: () => (
    <ToolCallBadge
      toolCall={{
        id: "call_1",
        name: "execute_code",
        arguments: { language: "python", code: "x" },
      }}
      result={{
        toolCallId: "call_1",
        success: false,
        output: null,
        error: "NameError",
      }}
    />
  ),
};
