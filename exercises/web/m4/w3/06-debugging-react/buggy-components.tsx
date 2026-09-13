"use client";
// Five buggy components. See README.md. Fix them without changing their props.
import { useEffect, useState } from "react";

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
          saved.push(draft);
          setSaved(saved);
        }}
      >
        Save
      </button>
      <ul aria-label="Saved jobs">
        {saved.map((title) => (
          <li key={title}>{title}</li>
        ))}
      </ul>
    </div>
  );
}

// ---------- 2 ----------
export function Stopwatch() {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    setInterval(() => {
      setSeconds(seconds + 1);
    }, 1000);
  }, []);
  return <p>Elapsed: {seconds}s</p>;
}

// ---------- 3 ----------
export type Note = { id: string; text: string };

export function NotesEditor({ initialNotes }: { initialNotes: Note[] }) {
  const [notes, setNotes] = useState(initialNotes);
  return (
    <ul>
      {notes.map((note, index) => (
        <li key={index}>
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
  const filters = { remote, minSalary: 0 };
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
  let adminToggle = null;
  if (user.isAdmin) {
    const [adminView, setAdminView] = useState(false);
    adminToggle = (
      <button type="button" aria-pressed={adminView} onClick={() => setAdminView((v) => !v)}>
        Admin view
      </button>
    );
  }
  const [unread] = useState(3);
  return (
    <div>
      <p>
        Hi, {user.name} ({unread} unread)
      </p>
      {adminToggle}
      <button type="button" aria-expanded={menuOpen} onClick={() => setMenuOpen((open) => !open)}>
        Account menu
      </button>
      {menuOpen && <p>{user.email}</p>}
    </div>
  );
}
