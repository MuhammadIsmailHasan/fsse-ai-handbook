// Shared schema (client + server). See README.md.
import { z } from "zod";

export const profileSchema = z.object({
  name: z.string(),
  email: z.string(),
  headline: z.string(),
  links: z.array(z.object({ label: z.string(), url: z.string() })),
});

export type ProfileValues = z.infer<typeof profileSchema>;
