# Web exercises (JavaScript, TypeScript, React, Next.js)

One Node project for every frontend exercise. Tests run in **Vitest** with **jsdom** (a simulated browser) and **Testing Library**.

```bash
cd exercises/web
npm install                            # once (Node 20+)
npx vitest run m4/w1/04-js-basics      # run one exercise
npx vitest m4/w1/04-js-basics          # watch mode: re-runs on every save
npx tsc --noEmit                       # type-check everything (TypeScript lessons)
```

Layout, same as the Python exercises:

```text
m4/w1/04-js-basics/
├── README.md            ← the task
├── basics.ts            ← you edit this
├── basics.test.ts       ← automatic checks (don't edit)
└── solution/            ← reference solution (open only after a real attempt)
```

Maintainers: `bash scripts/check-web-exercises.sh [filter]` verifies starters fail and solutions pass.
