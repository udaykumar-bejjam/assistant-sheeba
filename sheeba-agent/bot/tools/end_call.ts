import { defineTool } from "@cursor/bdk";
import { z } from "zod";

export default defineTool({
  description: "Politely end the phone call",
  execution: "server",
  effect: "write",
  inputSchema: z.object({
    reason: z.string().optional(),
  }),
  async execute({ reason }) {
    return {
      ok: true as const,
      ended: true as const,
      reason: reason ?? "completed",
    };
  },
});
