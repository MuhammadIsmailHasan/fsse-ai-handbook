"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useFieldArray, useForm, type FieldPath } from "react-hook-form";
import { profileSchema, type ProfileValues } from "./profile-schema";

export type ServerResult = void | { fieldErrors?: Partial<Record<"name" | "email" | "headline", string>>; message?: string };

const MAX_LINKS = 5;

export function ProfileForm({ defaultValues, onSubmit }: { defaultValues: ProfileValues; onSubmit: (values: ProfileValues) => Promise<ServerResult> }) {
  const [saved, setSaved] = useState(false);
  const {
    register,
    control,
    handleSubmit,
    setError,
    reset,
    getFieldState,
    formState: { errors, isSubmitting },
  } = useForm<ProfileValues>({ resolver: zodResolver(profileSchema), defaultValues, mode: "onTouched" });
  const { fields, append, remove } = useFieldArray({ control, name: "links" });

  // One helper keeps every field accessible in the same way.
  const a11y = (name: FieldPath<ProfileValues>) => {
    const { error } = getFieldState(name);
    return error ? { "aria-invalid": true as const, "aria-describedby": `${name}-error` } : {};
  };
  const errorText = (name: FieldPath<ProfileValues>) => {
    const { error } = getFieldState(name);
    return error?.message ? <p id={`${name}-error`}>{error.message}</p> : null;
  };

  const submit = handleSubmit(async (values) => {
    setSaved(false);
    const result = await onSubmit(values);
    if (result?.fieldErrors || result?.message) {
      for (const [field, message] of Object.entries(result.fieldErrors ?? {})) {
        setError(field as keyof NonNullable<typeof result.fieldErrors>, { type: "server", message });
      }
      if (result.message) setError("root.server", { type: "server", message: result.message });
      return;
    }
    reset(values);
    setSaved(true);
  });

  return (
    <form onSubmit={submit} noValidate>
      {errors.root?.server && <p role="alert">{errors.root.server.message}</p>}
      {saved && <p role="status">Profile saved</p>}

      <label htmlFor="name">Name</label>
      <input id="name" {...register("name")} {...a11y("name")} />
      {errorText("name")}

      <label htmlFor="email">Email</label>
      <input id="email" type="email" {...register("email")} {...a11y("email")} />
      {errorText("email")}

      <label htmlFor="headline">Headline</label>
      <input id="headline" {...register("headline")} {...a11y("headline")} />
      {errorText("headline")}

      <fieldset>
        <legend>Links</legend>
        {fields.map((field, index) => (
          // field.id (not index) is the key: removing a row keeps the other inputs' state.
          <div key={field.id}>
            <label htmlFor={`links.${index}.label`}>{`Link ${index + 1} label`}</label>
            <input id={`links.${index}.label`} {...register(`links.${index}.label`)} {...a11y(`links.${index}.label`)} />
            {errorText(`links.${index}.label`)}
            <label htmlFor={`links.${index}.url`}>{`Link ${index + 1} URL`}</label>
            <input id={`links.${index}.url`} type="url" {...register(`links.${index}.url`)} {...a11y(`links.${index}.url`)} />
            {errorText(`links.${index}.url`)}
            <button type="button" onClick={() => remove(index)}>{`Remove link ${index + 1}`}</button>
          </div>
        ))}
        <button type="button" disabled={fields.length >= MAX_LINKS} onClick={() => append({ label: "", url: "" })}>
          Add link
        </button>
      </fieldset>

      <button type="submit" disabled={isSubmitting}>
        Save profile
      </button>
    </form>
  );
}
