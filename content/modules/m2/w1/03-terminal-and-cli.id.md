---
title: "Terminal & CLI"
summary: Bekerja percaya diri di terminal — navigasi, cari, gabung perintah, baca variabel lingkungan, dan tulis skrip shell kecil.
sourceHash: f678b6a18ef2
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **terminal**, **shell**, dan **CLI**
- Navigasi dan kelola file dengan cepat
- Cari file dan teks (`find`, `grep`, `rg`)
- **Pipe** dan **redirection**: gabung perintah kecil jadi perintah hebat
- **Environment variable**, `PATH`, exit code, dan proses berjalan
- Tulis skrip **shell** kecil dan aman

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Terminal** | Jendela tempat kamu mengetik perintah |
| **Shell** | Program di dalamnya yang memahami perintahmu (bash, zsh) |
| **CLI** | Program yang kamu kendalikan dengan mengetik, bukan klik |
| **Working directory** | Folder yang sedang kamu berada — tempat perintah berlaku |
| **Pipe (`\|`)** | Menyalurkan hasil satu perintah ke perintah berikutnya |
| **Redirection (`>`, `>>`)** | Mengalihkan hasil ke file, bukan layar |
| **Environment variable** | Nilai bernama yang bisa dibaca program (`DATABASE_URL`) |
| **`PATH`** | Daftar folder tempat shell mencari perintah |
| **Exit code** | Angka yang dikembalikan perintah: 0 berarti sukses |
| **Shell script** | File yang berisi kumpulan perintah untuk dijalankan lagi |

## 🧠 Ide besarnya

Interface grafis itu seperti **menu restoran dengan gambar**: mudah, tapi kamu cuma bisa pesan yang tercetak di sana. Terminal itu seperti **bicara langsung dengan koki**: awalnya kamu harus pelajari kata-katanya, tapi kemudian kamu bisa minta persis apa yang mau — dan tulis pesanan itu untuk diulangi besok (skrip).

:term[CLI]{bahasa="Command Line Interface — cara mengendalikan program dengan mengetik perintah"} adalah alat developer untuk menjalankan server, tes, Git, Docker, database, dan deploy ke cloud. Server di production bahkan tidak ada layarnya.

## ❓ Kenapa ini penting

- **Otomasi**: apa pun yang kamu ketik bisa disimpan dalam skrip dan dijalankan persis sama lagi.
- **Komposisi**: alat kecil (`grep`, `sort`, `wc`) saling terhubung seperti Lego menjadi jawaban yang tidak ada dalam satu aplikasi.
- **Kerja jauh**: kamu kelola server cloud dan container lewat shell.
- **Kecepatan**: setelah tahu kata-katanya, banyak tugas lebih cepat daripada klik.

Tanpa terminal:

- Setiap README alat (`npm install`, `docker compose up`, `uv run pytest`) terasa menakutkan.
- Debug server production lewat SSH jadi mustahil.
- Kamu klik 400 file log tangan daripada jalankan satu `grep`.
- Kamu copy perintah dari internet seperti `rm -rf $DIR/` tanpa mengerti — dan `$DIR` kosong. 💀

## 📖 Langkah demi langkah

### 1. Terminal, shell, prompt

- **Terminal** — jendelanya (Terminal, iTerm2, Windows Terminal, terminal VS Code)
- **Shell** — program yang mengartikan perintahmu (`zsh` di macOS, `bash` di Linux, PowerShell di Windows; pakai WSL untuk shell Linux di Windows)
- **Prompt** — tempat kamu mengetik, misalnya `ismail@mac fsse-handbook %`

Struktur perintah:

```bash
ls   -la    ~/projects
│    │      └── argument (what to act on)
│    └── options/flags (how)
└── command (what)
```

`command --help` atau `man command` tunjukkan cara pakai. Tekan `Tab` untuk autolengkapi, `↑` untuk riwayat, `Ctrl R` untuk cari riwayat, `Ctrl C` untuk hentikan perintah yang sedang jalan.

### 2. Navigasi dan file

| Perintah | Fungsi |
|---|---|
| `pwd` | tampilkan folder sekarang |
| `ls -la` | daftar file, termasuk yang tersembunyi, dengan detail |
| `cd path` · `cd ..` · `cd ~` · `cd -` | pindah folder · atas · rumah · sebelumnya |
| `mkdir -p a/b/c` | buat folder bertingkat |
| `touch file.txt` | buat file kosong |
| `cp src dst` · `cp -r dir dst` | copy file · folder |
| `mv old new` | pindah atau ubah nama |
| `rm file` · `rm -r dir` | hapus (**tidak ada tempat sampah!**) |
| `cat file` · `less file` · `head -n 20` · `tail -f app.log` | tampilkan · halaman · 20 baris awal · ikuti log yang bertambah |

Path: **absolut** dimulai dari `/` (`/Users/ismail/…`); **relatif** dimulai dari tempat kamu sekarang (`./data/jobs.csv`, `../other`).

### 3. Cari sesuatu

```bash
find . -name "*.py" -not -path "./.venv/*"      # files by name
grep -rn "jwt_required" app/                   # text inside files, with line numbers
grep -ri "error" logs/ | wc -l                 # count matching lines, case-insensitive
rg "def create_app"                            # ripgrep: faster, respects .gitignore
```

### 4. Pipe dan redirection

Pipe adalah **sabuk penghubung antar mesin**: setiap perintah mengerjakan satu tugas kecil lalu lanjutkan hasilnya. Itulah kenapa alat kecil lebih hebat daripada satu program besar.

Setiap perintah membaca **input** dan menulis **output**. Pipe `|` menyalurkan output satu perintah ke input perintah berikutnya:

```bash
cat access.log | grep " 500 " | wc -l
```

"Hitung server error di log." Tiga alat kecil, satu jawaban.

Sebuah pipeline klasik — 5 path paling diminta:

```bash
cut -d' ' -f7 access.log | sort | uniq -c | sort -rn | head -5
```

| Simbol | Maksudnya |
|---|---|
| `a \| b` | output `a` → input `b` |
| `> file` | tulis output ke file (**timpa**) |
| `>> file` | tambahkan output ke file |
| `2> errors.txt` | tulis **error** output ke file |
| `&> all.txt` | output dan error |
| `a && b` | jalankan `b` cuma kalau `a` **sukses** |
| `a \|\| b` | jalankan `b` cuma kalau `a` **gagal** |

### 5. Exit code

Setiap perintah mengembalikan angka saat selesai: `0` = sukses, angka lain = gagal. `echo $?` tunjukkan yang terakhir. Tes, CI pipeline, dan `&&` semua bergantung pada ini. (CLI CareerPilot-mu mengembalikan `1` untuk file tidak ketemu — sekarang kamu tahu kenapa itu penting.)

### 6. Environment variable dan PATH

```bash
export DATABASE_URL="postgresql://localhost:5491/careerpilot"
echo "$DATABASE_URL"
env | grep DATABASE
```

- Environment variable atur program **tanpa ubah kode** — kamu akan pakainya untuk setiap secret dan pengaturan (Week 6).
- `PATH` adalah daftar folder tempat shell mencari perintah. `which python` tunjukkan mana yang jalan. "command not found" biasanya berarti tidak terinstall atau tidak ada di `PATH`.

### 7. Proses dan port

```bash
lsof -i :5091          # what is using port 5091? (macOS/Linux)
ps aux | grep flask    # find a running process
kill <PID>             # stop it politely
```

Berguna saat "port sudah dipakai" muncul — itulah kenapa handbook ini pakai port bukan default.

### 8. Skrip shell kecil dan aman

Skrip adalah sesi terminal kemarin, ditulis. Baris keselamatan di awal adalah sabuk pengaman: henti di kesalahan pertama, dan anggap variabel tidak diatur sebagai kesalahan daripada string kosong.

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

Jalankan dengan `bash error_count.sh app.log`, atau `chmod +x error_count.sh` lalu `./error_count.sh app.log`.

:::warning[Kapan stop pakai bash]
Skrip shell bagus untuk gabung perintah (< ~50 baris). Kalau butuh struktur data, logika kompleks, atau tes, tulis **Python** sebagai gantinya.
:::

### Pilih pengaturanmu

Setiap opsi di sini ada trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Terminal | bisa di-script, cepat, ramah jarak jauh, bisa digabung | ada kurva belajar; perintah merusak tidak bisa undo |
| Alat GUI | mudah ditemukan, visual | tidak bisa diulangi atau otomasi |
| Skrip Bash | ada di mana-mana, glue bagus | rawan kesalahan logika kompleks, jebakan tanda kutip |
| Skrip Python | mudah dibaca, bisa di-test, lintas platform | perlu sedikit lebih banyak setup |

- ✅ Jalankan alat dev, cari kode/log, ulangi langkah setup, server dan container.
- ✅ Simpan perintah yang kamu jalankan tiga kali ke skrip atau `Makefile`/`package.json` script.
- 🚫 Jangan jalankan perintah yang tidak kamu mengerti — terutama dengan `sudo`, `rm -rf`, atau pipe URL ke `sh`.
- 🚫 Jangan tulis program bash 300-baris; pindah ke Python.

## ⚠️ Kesalahan umum

- Variabel tanpa tanda kutip yang ada spasi.
- `>` secara tidak sengaja timpa file yang harusnya ditambah.
- Jalankan perintah di folder salah (`pwd` dulu!).
- Lupa bahwa `rm` tidak ada tempat sampahnya.
- Bingungkan `python` di `PATH` dengan virtual environment proyek.

:::revoshop
Buka `docker/entrypoint.sh` di RevoShop. Jelaskan tiap baris: Apakah ia pakai `set -e` atau sejenis? Bagaimana ia tunggu database (hint: `netcat-openbsd` sudah dipasang di `Dockerfile`)? Apa yang terjadi kalau migrasi gagal — container berhenti? Kemudian jalankan `grep -rn "jwt_required" app/routes | wc -l` di repo-mu: berapa protected endpoint yang ada?
:::

## 🏆 Praktik terbaik

- [ ] Mulai skrip dengan `#!/usr/bin/env bash` dan `set -euo pipefail`.
- [ ] **Selalu beri tanda kutip pada variabel**: `"$FILE"`, bukan `$FILE` (spasi di nama rusak semuanya).
- [ ] Validasi argument dan tampilkan cara pakai; kirim error ke stderr (`>&2`) dan keluar dengan non-zero.
- [ ] Lebih suka **dry run** sebelum operasi merusak (misalnya `echo` perintah duluan, atau `rm -i`).
- [ ] Simpan secret di environment variable atau `.env` yang diabaikan git, jangan ketik ke skrip atau shell history yang dibagikan.
- [ ] Pakai `rg` (ripgrep) dan `fd` untuk kecepatan; pelajari pencarian riwayat `Ctrl R`.
- [ ] Letakkan perintah proyek di satu tempat (`Makefile`, `package.json` script, `justfile`) jadi teammates jalankan yang sama.
- [ ] Cek skrip dengan **ShellCheck** — ia tangkap tanda kutip dan bug logika.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan pipe (`|`) pada non-programmer menggunakan lini produksi pabrik. Kemudian jelaskan dalam satu kalimat kenapa exit code penting untuk otomasi.

## 📐 Rancang

API Flask-mu tulis log seperti:

```text
2026-09-13T10:02:11 INFO GET /api/jobs 200 34ms
2026-09-13T10:02:12 ERROR POST /api/applications 500 120ms
```

Rancang **pipeline satu baris** (tidak perlu jalankan) untuk:
1. Berapa baris `ERROR` di `app.log`?
2. Tiga endpoint (method + path) dengan paling banyak response 500
3. Simpan semua baris dari 10:00 sampai 10:59 ke `ten_oclock.log`

:::quiz
Lihat pipeline yang mungkin

```bash
grep -c " ERROR " app.log
grep " 500 " app.log | awk '{print $3, $4}' | sort | uniq -c | sort -rn | head -3
grep "T10:" app.log > ten_oclock.log
```

`awk '{print $3, $4}'` tampilkan field ke-3 dan ke-4 yang dipisahkan spasi (method dan path).
:::

### 📝 Checklist review mandiri

- [ ] Pipeline-ku filter dulu, lalu hitung/sort
- [ ] Aku pakai `>` (timpa) dengan sengaja untuk file baru
- [ ] Aku bisa jelaskan setiap perintah di rantai

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w1/03-terminal" ai="no-ai" title="Skrip detektif log"}
Tulis dua bash script (detail di folder README):

- `organize.sh DIR` — sortir file di folder berantakan ke `logs/`, `data/`, dan `images/`
- `error_report.sh LOG_FILE` — tampilkan banyaknya error dan 3 endpoint yang paling sering gagal

Tes menjalankan skrip-mu di folder sementara. Mulai keduanya dengan `set -euo pipefail` dan beri tanda kutip setiap variabel.
:::

:::hints
- Loop file dengan aman: `for file in "$DIR"/*.log; do …; done` — dan tangani "tidak cocok apa pun" dengan `shopt -s nullglob`.
- `mkdir -p` tidak gagal kalau folder sudah ada.
- Untuk laporan, pakai ulang ide pipeline dari *Rancang*.
- `${1:?message}` buat argument wajib ada.
:::

### 🏆 Tantangan lebih

Pasang [ShellCheck](https://www.shellcheck.net/) (`brew install shellcheck`) dan buat kedua skrip bebas peringatan.

## ✅ Cek cepat

:::quiz
Apa bedanya `>` dan `>>`?

`>` ganti isi file; `>>` tambahkan ke akhir.
:::

:::quiz
Apa yang `set -euo pipefail` lakukan?

`-e` keluar saat ada perintah gagal, `-u` anggap variabel tidak diatur sebagai error, dan `pipefail` buat pipeline gagal kalau ada perintah di dalamnya gagal — jadi skrip berhenti daripada terus dalam keadaan rusak.
:::

:::quiz
Kamu dapat "command not found: uv". Apa dua penyebab paling mungkin?

Tidak terinstall, atau terinstall di folder yang tidak di `PATH` (restart terminal atau tambah folder ke `PATH`).
:::


## 📚 Lanjut belajar

- [The Missing Semester (MIT): The Shell & Shell Tools](https://missing.csail.mit.edu/2020/shell-tools/)
- [ShellCheck](https://www.shellcheck.net/)
- [ripgrep user guide](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md)
