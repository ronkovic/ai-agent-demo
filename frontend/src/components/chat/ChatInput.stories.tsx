import type { Meta, StoryObj } from "@storybook/react";
import { ChatInput } from "./ChatInput";

const meta: Meta<typeof ChatInput> = {
  title: "Chat/ChatInput",
  component: ChatInput,
  parameters: {
    layout: "padded",
  },
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof ChatInput>;

export const Default: Story = {
  args: {
    placeholder: "Type a message...",
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
    placeholder: "Cannot send message...",
  },
};

export const WithText: Story = {
  args: {
    placeholder: "Type a message...",
  },
  play: async () => {
    // In a real interaction test we would type here, but for static story just showing state is hard without controlled prop or initial state prop which component doesn't have.
    // So we just rely on Default.
  },
};
