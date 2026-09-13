"use server";

import { redirect } from "next/navigation";
import { z } from "zod";
import { InvalidCredentials, loginWithFlask } from "../../lib/flask-auth";
import { safeNextPath } from "../../lib/safe-redirect";
import { createSession, deleteSession } from "../../lib/session";

export type LoginState = { message: string | null };

const credentialsSchema = z.object({ email: z.email(), password: z.string().min(1) });

export async function login(_previousState: LoginState, formData: FormData): Promise<LoginState> {
  const parsed = credentialsSchema.safeParse({ email: formData.get("email"), password: formData.get("password") });
  if (!parsed.success) return { message: "Enter your email and password" };

  try {
    const { accessToken, user } = await loginWithFlask(parsed.data.email, parsed.data.password);
    await createSession(user, accessToken);
  } catch (error) {
    // Same message for "no such user" and "wrong password" → no account enumeration.
    if (error instanceof InvalidCredentials) return { message: "Invalid email or password" };
    throw error;
  }

  redirect(safeNextPath(formData.get("next")));
}

export async function logout(): Promise<void> {
  await deleteSession();
  redirect("/login");
}
