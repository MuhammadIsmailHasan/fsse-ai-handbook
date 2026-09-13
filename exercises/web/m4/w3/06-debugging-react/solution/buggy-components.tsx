"use client";
// Five buggy components — reference fixes.
import { useEffect, useMemo, useState } from "react";

// ---------- 1 ----------
export function SavedList() {
  const [saved, setSaved] = useState<string[]>([]);
  const [draft, setDraft] = useState("");
  return (
    <div>
      <label htmlFor="job-title">Job title</label>
      <input id="job-title" value={draft} onChange={(e) => setDraft(e.target.value)} />
      <button
        type="button"
        onClick={() => {
          // cause: push mutated the same array, so React saw no change → fix: create a new array
          setSaved((previous) => [...previous, draft]);
        }}
      >
        Save
      </button>
      <ul aria-label="Saved jobs">
        {saved.map((title, index) => (
          <li key={`${index}-${title}`}>{title}</li>
        ))}
      </ul>
    </div>
  );
}

// ---------- 2 ----------
export function Stopwatch() {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    // cause: stale closure (seconds was always 0) and no cleanup → fix: updater function + clearInterval on unmount
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, []);
  return <p>Elapsed: {seconds}s</p>;
}

// ---------- 3 ----------
export type Note = { id: string; text: string };

export function NotesEditor({ initialNotes }: { initialNotes: Note[] }) {
  const [notes, setNotes] = useState(initialNotes);
  return (
    <ul>
      {notes.map((note) => (
        // cause: index keys made React reuse the first <li> (and its input state) for B → fix: stable id keys
        <li key={note.id}>
          <input aria-label={`Note ${note.id}`} defaultValue={note.text} />
          <button type="button" onClick={() => setNotes(notes.filter((n) => n.id !== note.id))}>
            Delete {note.id}
          </button>
        </li>
      ))}
    </ul>
  );
}

// ---------- 4 ----------
export type Filters = { remote: boolean; minSalary: number };

export function FiltersPanel({ onChange }: { onChange: (filters: Filters) => void }) {
  const [remote, setRemote] = useState(false);
  // cause: a new filters object every render re-ran the effect, whose parent update re-rendered… forever → fix: memoize on real inputs
  const filters = useMemo(() => ({ remote, minSalary: 0 }), [remote]);
  useEffect(() => {
    onChange(filters);
  }, [filters, onChange]);
  return (
    <label>
      <input type="checkbox" checked={remote} onChange={(e) => setRemote(e.target.checked)} /> Remote only
    </label>
  );
}

// ---------- 5 ----------
export type User = { name: string; email: string; isAdmin: boolean };

export function ProfileHeader({ user }: { user: User }) {
  const [menuOpen, setMenuOpen] = useState(false);
  // cause: a hook inside `if` changed the hook order when isAdmin changed → fix: always call hooks, make the OUTPUT conditional
  const [adminView, setAdminView] = useState(false);
  const [unread] = useState(3);
  return (
    <div>
      <p>
        Hi, {user.name} ({unread} unread)
      </p>
      {user.isAdmin && (
        <button type="button" aria-pressed={adminView} onClick={() => setAdminView((v) => !v)}>
          Admin view
        </button>
      )}
      <button type="button" aria-expanded={menuOpen} onClick={() => setMenuOpen((open) => !open)}>
        Account menu
      </button>
      {menuOpen && <p>{user.email}</p>}
    </div>
  );
}
