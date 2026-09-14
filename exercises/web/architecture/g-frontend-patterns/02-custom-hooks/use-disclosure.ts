// See README.md.
export function useDisclosure(initial = false) {
  return { isOpen: initial, open() {}, close() {}, toggle() {} };
}
