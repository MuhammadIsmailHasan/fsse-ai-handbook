// Accessible widgets — reference solution.

export function createTabs(root, tabs) {
  const tablist = document.createElement("div");
  tablist.setAttribute("role", "tablist");
  const buttons = [];
  const panels = [];

  tabs.forEach(({ id, label, content }) => {
    const button = document.createElement("button");
    button.type = "button";
    button.id = `tab-${id}`;
    button.setAttribute("role", "tab");
    button.setAttribute("aria-controls", `panel-${id}`);
    button.textContent = label;
    buttons.push(button);
    tablist.append(button);

    const panel = document.createElement("div");
    panel.id = `panel-${id}`;
    panel.setAttribute("role", "tabpanel");
    panel.setAttribute("aria-labelledby", `tab-${id}`);
    panel.textContent = content;
    panels.push(panel);
  });

  function select(index, { focus = false } = {}) {
    buttons.forEach((button, i) => {
      const selected = i === index;
      button.setAttribute("aria-selected", String(selected));
      button.tabIndex = selected ? 0 : -1; // roving tabindex: only the selected tab is in the Tab order
      panels[i].hidden = !selected;
    });
    if (focus) buttons[index].focus();
  }

  tablist.addEventListener("click", (event) => {
    const index = buttons.indexOf(event.target.closest('[role="tab"]'));
    if (index >= 0) select(index);
  });

  tablist.addEventListener("keydown", (event) => {
    const current = buttons.indexOf(document.activeElement);
    if (current < 0) return;
    const last = buttons.length - 1;
    const next = { ArrowRight: current === last ? 0 : current + 1, ArrowLeft: current === 0 ? last : current - 1, Home: 0, End: last }[event.key];
    if (next === undefined) return;
    event.preventDefault();
    select(next, { focus: true });
  });

  root.append(tablist, ...panels);
  select(0);
}

const RULES = {
  email: { test: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v), message: "Enter a valid email address" },
  password: { test: (v) => v.length >= 8, message: "Password must be at least 8 characters" },
};

export function validateSignup(form) {
  let firstInvalid = null;
  for (const [field, rule] of Object.entries(RULES)) {
    const input = form.querySelector(`#${field}`);
    const error = form.querySelector(`#${field}-error`);
    if (rule.test(input.value)) {
      input.removeAttribute("aria-invalid");
      input.removeAttribute("aria-describedby");
      error.textContent = "";
    } else {
      input.setAttribute("aria-invalid", "true");
      input.setAttribute("aria-describedby", `${field}-error`);
      error.textContent = rule.message;
      firstInvalid ??= input;
    }
  }
  firstInvalid?.focus();
  return firstInvalid === null;
}
