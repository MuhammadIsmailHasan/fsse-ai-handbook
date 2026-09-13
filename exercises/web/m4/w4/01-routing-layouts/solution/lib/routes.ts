export function routeFromFile(file: string): string | null {
  const segments = file.split("/");
  if (segments[0] !== "app") return null;
  const fileName = segments.at(-1) ?? "";
  if (!/^(page\.(tsx|jsx|js)|route\.(ts|js))$/.test(fileName)) return null;
  const folders = segments.slice(1, -1);
  if (folders.some((folder) => folder.startsWith("_"))) return null; // private folders aren't routable
  const urlSegments = folders.filter((folder) => !/^\(.+\)$/.test(folder)); // route groups vanish from the URL
  return "/" + urlSegments.join("/");
}
