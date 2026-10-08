import { defineTool } from "@cursor/bdk";
import { z } from "zod";

export default defineTool({
  description: "Create a callback request for Uday",
  execution: "server",
  effect: "write",
  inputSchema: z.object({
    note: z.string().min(1),
    preferred_time: z.string().optional(),
  }),
  async execute({ note, preferred_time }) {
    return {
      ok: true as const,
      note,
      preferred_time: preferred_time ?? null,
    };
  },
});
