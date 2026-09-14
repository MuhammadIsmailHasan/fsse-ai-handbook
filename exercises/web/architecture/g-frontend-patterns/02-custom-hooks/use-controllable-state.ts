// See README.md.
export function useControllableState<T>(options: { value?: T; defaultValue: T; onChange?: (value: T) => void }): [T, (next: T | ((prev: T) => T)) => void] {
  return [options.defaultValue, () => {}];
}
