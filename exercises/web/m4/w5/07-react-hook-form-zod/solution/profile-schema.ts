import { z } from "zod";

export const profileSchema = z.object({
  name: z.string().trim().min(2, "Name must be at least 2 characters"),
  email: z.email("Enter a valid email"),
  headline: z.string().trim().max(120, "Keep your headline under 120 characters"),
  links: z
    .array(
      z.object({
        label: z.string().trim().min(1, "Label is required"),
        url: z.url("Enter a full URL, e.g. https://…"),
      }),
    )
    .max(5),
});

export type ProfileValues = z.infer<typeof profileSchema>;
