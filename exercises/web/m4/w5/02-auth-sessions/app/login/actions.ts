// Login / logout Server Actions. See README.md.
export type LoginState = { message: string | null };

export async function login(previousState: LoginState, formData: FormData): Promise<LoginState> {
  throw new Error("TODO");
}

export async function logout(): Promise<void> {
  throw new Error("TODO");
}
