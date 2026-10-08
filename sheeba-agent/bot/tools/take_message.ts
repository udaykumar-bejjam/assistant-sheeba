import { defineTool } from "@cursor/bdk";
import { z } from "zod";

export default defineTool({
  description: "Take a message for Uday from the caller",
  execution: "server",
  effect: "write",
  inputSchema: z.object({
    message: z.string().min(1),
  }),
  async execute({ message }) {
    return {
      ok: true as const,
      recorded: true as const,
      messagePreview: message.slice(0, 120),
    };
  },
});
