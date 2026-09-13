/** Test helper: compile a Tailwind CSS v4 entry file (scanning the folder for class names). */
import tailwind from "@tailwindcss/postcss";
import { readFileSync } from "node:fs";
import { dirname } from "node:path";
import postcss from "postcss";

export async function compileTailwind(cssFile: string): Promise<string> {
  const result = await postcss([tailwind({ base: dirname(cssFile) })]).process(readFileSync(cssFile, "utf8"), { from: cssFile });
  return result.css;
}
