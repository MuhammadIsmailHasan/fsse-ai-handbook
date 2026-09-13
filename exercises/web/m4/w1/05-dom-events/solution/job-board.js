// Vanilla DOM job board — reference solution.

/**
 * @param {HTMLElement} root
 * @param {{ id: number, title: string, company: string, city: string }[]} jobs
 * @returns {() => void} cleanup
 */
export function mountJobBoard(root, jobs) {
  const saved = new Set();
  let query = "";

  const form = document.createElement("form");
  form.setAttribute("role", "search");
  const label = document.createElement("label");
  label.htmlFor = "job-search";
  label.textContent = "Search jobs";
  const input = document.createElement("input");
  input.id = "job-search";
  input.type = "search";
  form.append(label, input);

  const status = document.createElement("p");
  status.setAttribute("aria-live", "polite");
  const list = document.createElement("ul");
  const empty = document.createElement("p");
  empty.className = "empty";

  root.append(form, status, list);

  function render() {
    const needle = query.trim().toLowerCase();
    const visible = jobs.filter((job) => `${job.title} ${job.company}`.toLowerCase().includes(needle));

    list.replaceChildren(
      ...visible.map((job) => {
        const item = document.createElement("li");
        item.dataset.id = String(job.id);
        const title = document.createElement("h2");
        title.textContent = job.title; // textContent: data is never parsed as HTML
        const meta = document.createElement("p");
        meta.textContent = `${job.company} · ${job.city}`;
        const button = document.createElement("button");
        button.type = "button";
        const isSaved = saved.has(job.id);
        button.setAttribute("aria-pressed", String(isSaved));
        button.textContent = isSaved ? "Saved" : "Save";
        item.append(title, meta, button);
        return item;
      }),
    );

    status.textContent = `${visible.length} jobs · ${saved.size} saved`;
    if (visible.length === 0) {
      empty.textContent = `No jobs match "${query}"`;
      list.after(empty);
    } else {
      empty.remove();
    }
  }

  const onInput = () => {
    query = input.value;
    render();
  };
  const onSubmit = (/** @type {Event} */ event) => event.preventDefault();
  // Event delegation: one listener on the list handles every button, even ones rendered later.
  const onClick = (/** @type {MouseEvent} */ event) => {
    const button = /** @type {HTMLElement} */ (event.target).closest("button");
    const item = button?.closest("li");
    if (!button || !item) return;
    const id = Number(item.dataset.id);
    if (saved.has(id)) saved.delete(id);
    else saved.add(id);
    render();
  };

  input.addEventListener("input", onInput);
  form.addEventListener("submit", onSubmit);
  list.addEventListener("click", onClick);
  render();

  return () => {
    input.removeEventListener("input", onInput);
    form.removeEventListener("submit", onSubmit);
    list.removeEventListener("click", onClick);
    form.remove();
    status.remove();
    list.remove();
    empty.remove();
  };
}
