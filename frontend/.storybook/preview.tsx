import type { Preview } from "@storybook/react";

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    backgrounds: {
      default: "dark",
      values: [
        { name: "dark", value: "#0a0a0f" },
        { name: "surface", value: "#12121a" },
        { name: "card", value: "#1a1a2e" },
      ],
    },
    layout: "padded",
  },
  tags: ["autodocs"],
};

export default preview;