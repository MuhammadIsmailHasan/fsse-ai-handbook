---
title: "Terminal & CLI"
summary: Work confidently in the terminal — navigate, search, pipe commands together, read environment variables, and write small shell scripts.
type: lesson
source: core
sourceRef: "M2 · W1 · L3"
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 150
tags: [terminal, shell, bash, cli, tooling]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What the **terminal**, **shell** and **CLI** are
- Navigating and managing files quickly
- Searching files and text (`find`, `grep`, `rg`)
- **Pipes** and **redirection**: combining small commands into powerful ones
- **Environment variables**, `PATH`, exit codes, and running processes
- Writing a small, safe **shell script**

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Terminal** | The window where you type commands | Jendela perintah |
| **Shell** | The program inside it that understands what you type (bash, zsh) | Penerjemah perintah |
| **CLI** | A program you control by typing instead of clicking | Program berbasis teks |
| **Working directory** | The folder your commands act on right now | Folder tempat kamu berada |
| **Pipe (`\|`)** | Sending one command's output into the next command | Menyalurkan hasil ke perintah lain |
| **Redirection (`>`, `>>`)** | Sending output into a file instead of the screen | Mengalihkan hasil ke file |
| **Environment variable** | A named value programs can read (`DATABASE_URL`) | Nilai bernama untuk program |
| **`PATH`** | The list of folders the shell searches for a command | Daftar folder pencarian perintah |
| **Exit code** | A number a command returns: 0 means success | Kode hasil perintah |
| **Shell script** | A file of commands you can run again later | Kumpulan perintah tersimpan |

## 🧠 The big idea

A graphical interface is a **restaurant menu with pictures**: easy, but you can only order what's printed on it. The terminal is **talking directly to the chef**: at first you must learn the words, but then you can ask for exactly what you want — and write the order down to repeat it tomorrow (a script).

:term[CLI]{bahasa="Command Line Interface — cara mengendalikan program dengan mengetik perintah"} tools are how developers run servers, tests, Git, Docker, databases and cloud deployments. Servers in production don't even have a screen.

## ❓ Why it matters

- **Automation**: anything you type can be saved in a script and repeated exactly.
- **Composition**: small tools (`grep`, `sort`, `wc`) snap together like Lego into answers no single app gives you.
- **Remote work**: you manage cloud servers and containers through a shell.
- **Speed**: once you know the words, many tasks are faster than clicking.

Without it:

- Every tool's README (`npm install`, `docker compose up`, `uv run pytest`) feels scary.
- Debugging a production server over SSH is impossible.
- You click through 400 log files by hand instead of running one `grep`.
- You copy a command from the internet like `rm -rf $DIR/` without understanding it… and `$DIR` is empty. 💀

## 📖 Step by step

### 1. Terminal, shell, prompt

- **Terminal** — the window (Terminal, iTerm2, Windows Terminal, the VS Code terminal)
- **Shell** — the program interpreting your commands (`zsh` on macOS, `bash` on Linux, PowerShell on Windows; use WSL for a Linux shell on Windows)
- **Prompt** — where you type, e.g. `ismail@mac fsse-handbook %`

Command anatomy:

```bash
ls   -la    ~/projects
│    │      └── argument (what to act on)
│    └── options/flags (how)
└── command (what)
```

`command --help` or `man command` shows usage. Press `Tab` to autocomplete, `↑` for history, `Ctrl R` to search history, `Ctrl C` to stop a running command.

### 2. Navigation and files

| Command | Does |
|---|---|
| `pwd` | print current directory |
| `ls -la` | list files, including hidden ones, with details |
| `cd path` · `cd ..` · `cd ~` · `cd -` | change directory · up · home · previous |
| `mkdir -p a/b/c` | create nested folders |
| `touch file.txt` | create an empty file |
| `cp src dst` · `cp -r dir dst` | copy file · folder |
| `mv old new` | move or rename |
| `rm file` · `rm -r dir` | delete (**no trash bin!**) |
| `cat file` · `less file` · `head -n 20` · `tail -f app.log` | print · page · first lines · follow a growing log |

Paths: **absolute** start at `/` (`/Users/ismail/…`); **relative** start from where you are (`./data/jobs.csv`, `../other`).

### 3. Finding things

```bash
find . -name "*.py" -not -path "./.venv/*"      # files by name
grep -rn "jwt_required" app/                   # text inside files, with line numbers
grep -ri "error" logs/ | wc -l                 # count matching lines, case-insensitive
rg "def create_app"                            # ripgrep: faster, respects .gitignore
```

### 4. Pipes and redirection

A pipe is a **conveyor belt between machines**: each command does one small job and passes the result on. That's why tiny tools beat one big program.

Every command reads **input** and writes **output**. The pipe `|` sends one command's output into the next command's input:

```bash
cat access.log | grep " 500 " | wc -l
```

"Count server errors in the log." Three tiny tools, one answer.

A classic analytics pipeline — top 5 most requested paths:

```bash
cut -d' ' -f7 access.log | sort | uniq -c | sort -rn | head -5
```

| Symbol | Meaning |
|---|---|
| `a \| b` | output of `a` → input of `b` |
| `> file` | write output to file (**overwrites**) |
| `>> file` | append output to file |
| `2> errors.txt` | write **error** output to a file |
| `&> all.txt` | output and errors |
| `a && b` | run `b` only if `a` **succeeded** |
| `a \|\| b` | run `b` only if `a` **failed** |

### 5. Exit codes

Every command returns a number when it finishes: `0` = success, anything else = failure. `echo $?` shows the last one. Tests, CI pipelines and `&&` all rely on this. (Your CareerPilot CLI returns `1` for a missing file — now you know why that matters.)

### 6. Environment variables and PATH

```bash
export DATABASE_URL="postgresql://localhost:5491/careerpilot"
echo "$DATABASE_URL"
env | grep DATABASE
```

- Environment variables configure programs **without changing code** — you'll use them for every secret and setting (Week 6).
- `PATH` is the list of folders the shell searches for commands. `which python` shows which one runs. "command not found" usually means it's not installed or not on `PATH`.

### 7. Processes and ports

```bash
lsof -i :5091          # what is using port 5091? (macOS/Linux)
ps aux | grep flask    # find a running process
kill <PID>             # stop it politely
```

Useful when "port already in use" appears — which is also why this handbook uses non-default ports.

### 8. A small, safe shell script

A script is yesterday's terminal session, written down. The safety lines at the top are the seatbelt: stop on the first error, and treat an unset variable as a mistake rather than an empty string.

```bash
#!/usr/bin/env bash
set -euo pipefail          # stop on errors, unset variables, and failures inside pipes

LOG_FILE="${1:?Usage: error_count.sh LOG_FILE}"   # require an argument

if [[ ! -f "$LOG_FILE" ]]; then
  echo "Error: file not found: $LOG_FILE" >&2
  exit 1
fi

count=$(grep -c "ERROR" "$LOG_FILE" || true)
echo "Errors: $count"
```

Run with `bash error_count.sh app.log`, or `chmod +x error_count.sh` then `./error_count.sh app.log`.

:::warning[When to stop using bash]
Shell scripts are great for gluing commands together (< ~50 lines). Once you need data structures, complex logic or tests, write **Python** instead.
:::

### Choosing your setup

Every option here is a trade-off:

| Choice | ✅ | ❌ |
|---|---|---|
| Terminal | scriptable, fast, remote-friendly, composable | learning curve; destructive commands have no undo |
| GUI tools | discoverable, visual | not repeatable or automatable |
| Bash script | available everywhere, great glue | error-prone for complex logic, quoting pitfalls |
| Python script | readable, testable, cross-platform | slightly more setup |

- ✅ Running dev tools, searching code/logs, repeatable setup steps, servers and containers.
- ✅ Save a command you ran three times into a script or a `Makefile`/`package.json` script.
- 🚫 Don't run commands you don't understand — especially with `sudo`, `rm -rf`, or piping a URL into `sh`.
- 🚫 Don't write 300-line bash programs; switch to Python.

## ⚠️ Common mistakes

- Unquoted variables with spaces.
- `>` accidentally overwriting a file you meant to append to.
- Running commands in the wrong directory (`pwd` first!).
- Forgetting that `rm` has no trash bin.
- Mixing up the `python` on `PATH` with the project's virtual environment.

:::revoshop
Open `docker/entrypoint.sh` in RevoShop. Explain each line: Does it use `set -e` or similar? How does it wait for the database (hint: `netcat-openbsd` is installed in the `Dockerfile`)? What happens if migrations fail — does the container stop? Then run `grep -rn "jwt_required" app/routes | wc -l` in your repo: how many protected endpoints do you have?
:::

## 🏆 Best practices

- [ ] Start scripts with `#!/usr/bin/env bash` and `set -euo pipefail`.
- [ ] **Always quote variables**: `"$FILE"`, not `$FILE` (spaces in names break things).
- [ ] Validate arguments and print usage; send errors to stderr (`>&2`) and exit non-zero.
- [ ] Prefer **dry runs** before destructive operations (e.g. `echo` the command first, or `rm -i`).
- [ ] Keep secrets in environment variables or a git-ignored `.env`, never typed into scripts or shell history you share.
- [ ] Use `rg` (ripgrep) and `fd` for speed; learn `Ctrl R` history search.
- [ ] Put project commands in one place (`Makefile`, `package.json` scripts, `justfile`) so teammates run the same thing.
- [ ] Check scripts with **ShellCheck** — it catches quoting and logic bugs.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain pipes (`|`) to a non-programmer using a factory production line. Then explain in one sentence why exit codes matter for automation.

## 📐 Design it

Your Flask API writes logs like:

```text
2026-09-13T10:02:11 INFO GET /api/jobs 200 34ms
2026-09-13T10:02:12 ERROR POST /api/applications 500 120ms
```

Design **one-line pipelines** (no need to run them) for:
1. How many `ERROR` lines are in `app.log`?
2. The 3 endpoints (method + path) with the most 500 responses
3. Save all lines from 10:00 to 10:59 into `ten_oclock.log`

:::quiz
Show possible pipelines

```bash
grep -c " ERROR " app.log
grep " 500 " app.log | awk '{print $3, $4}' | sort | uniq -c | sort -rn | head -3
grep "T10:" app.log > ten_oclock.log
```

`awk '{print $3, $4}'` prints the 3rd and 4th space-separated fields (method and path).
:::

### 📝 Self-review checklist

- [ ] My pipelines filter first, then count/sort
- [ ] I used `>` (overwrite) deliberately for the new file
- [ ] I can explain each command in the chain

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m2/w1/03-terminal" ai="no-ai" title="Log detective scripts"}
Write two bash scripts (details in the folder's README):

- `organize.sh DIR` — sorts files in a messy folder into `logs/`, `data/` and `images/`
- `error_report.sh LOG_FILE` — prints the number of errors and the top 3 failing endpoints

The tests run your scripts on temporary folders. Start both with `set -euo pipefail` and quote every variable.
:::

:::hints
- Loop over files safely: `for file in "$DIR"/*.log; do …; done` — and handle "no matches" with `shopt -s nullglob`.
- `mkdir -p` doesn't fail if the folder exists.
- For the report, reuse the pipeline idea from *Design it*.
- `${1:?message}` makes an argument required.
:::

### 🏆 Stretch goal

Install [ShellCheck](https://www.shellcheck.net/) (`brew install shellcheck`) and make both scripts warning-free.

## ✅ Quick check

:::quiz
What's the difference between `>` and `>>`?

`>` replaces the file's content; `>>` appends to the end.
:::

:::quiz
What does `set -euo pipefail` do?

`-e` exits on any failing command, `-u` treats unset variables as errors, and `pipefail` makes a pipeline fail if any command in it fails — so scripts stop instead of continuing in a broken state.
:::

:::quiz
You get "command not found: uv". What are the two most likely causes?

It isn't installed, or it's installed in a folder that isn't on your `PATH` (restart the terminal or add the folder to `PATH`).
:::


## 📚 Keep learning

- [The Missing Semester (MIT): The Shell & Shell Tools](https://missing.csail.mit.edu/2020/shell-tools/)
- [ShellCheck](https://www.shellcheck.net/)
- [ripgrep user guide](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md)
