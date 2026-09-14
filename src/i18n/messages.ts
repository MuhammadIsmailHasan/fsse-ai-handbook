/**
 * messages.ts — every piece of UI text, in English and Bahasa Indonesia.
 *
 * Lesson text lives in Markdown (`01-lesson.md` + `01-lesson.id.md`); this file is
 * only for the app around it: buttons, labels, page headers.
 *
 * Teaches:
 * - `as const` + `keyof typeof`: the English object DEFINES the list of keys,
 *   and `Record<MessageKey, string>` forces the Indonesian object to have every one.
 *   Forget a translation → TypeScript error, not a blank button.
 * - Tiny interpolation: "{count} done" + { count: 3 } → "3 done". No library needed.
 */

export const LOCALES = ['en', 'id'] as const
export type Locale = (typeof LOCALES)[number]

export const LOCALE_INFO: Record<Locale, { short: string; name: string; flag: string }> = {
  en: { short: 'EN', name: 'English', flag: '🇬🇧' },
  id: { short: 'ID', name: 'Bahasa Indonesia', flag: '🇮🇩' },
}

export const en = {
  // Layout
  'layout.skipToContent': 'Skip to content',
  'topbar.openNavigation': 'Open navigation',
  'topbar.search': 'Search',
  'sidebar.label': 'Handbook navigation',
  'sidebar.close': 'Close navigation',
  'sidebar.overview': 'Overview',
  'sidebar.course': 'Course',
  'sidebar.tracks': 'Tracks',
  'sidebar.projects': 'Projects',
  'sidebar.guidesAndApp': 'Guides & App',
  'nav.dashboard': 'Dashboard',
  'nav.roadmap': 'Roadmap',
  'nav.thisWeek': 'This Week',
  'nav.settings': 'Settings',
  'tree.expand': 'Expand {label}',
  'tree.collapse': 'Collapse {label}',
  'tree.comingSoon': 'Content coming soon',
  'targetRole.heading': '🎯 Target role',
  'targetRole.coreDone': 'Core lessons done',
  'targetRole.core': '{done}/{total} core',

  // Theme & language
  'theme.light': 'Light',
  'theme.dark': 'Dark',
  'theme.system': 'System',
  'theme.toggle': 'Theme: {current}. Switch to {next}.',
  'theme.title': 'Theme: {current}',
  'language.toggle': 'Language: {current}. Switch to {next}.',
  'language.title': 'Language / Bahasa',

  // Roles and importance levels
  'level.core': 'Core',
  'level.recommended': 'Recommended',
  'level.optional': 'Optional',
  'level.none': 'Not needed',
  'role.aiFs.description': 'Full-Stack + AI Engineer combined',
  'role.fs.description': 'Backend + frontend',
  'role.ai.description': 'Building products with LLMs',
  'role.be.description': 'APIs, databases, services',
  'role.fe.description': 'UI, React, Next.js',
  'role.ops.description': 'CI/CD, cloud, infrastructure',
  'roles.importance': 'Importance per role',

  // Lesson page
  'lesson.loading': 'Loading lesson…',
  'lesson.module': 'Module {number} · {title}',
  'lesson.project': 'Project',
  'lesson.guide': 'Guide',
  'lesson.sourceRef': '📘 the bootcamp ref · {ref}',
  'lesson.bonus': '🔥 Bonus',
  'lesson.split': '✂️ Split lesson',
  'lesson.studyHours': '⏱️ ~{hours} h study',
  'lesson.readMinutes': '📖 {minutes} min read',
  'lesson.reviewed': '🕒 Reviewed {date}',
  'lesson.awsFree': '🟢 AWS: Free',
  'lesson.awsSmall': '🟡 AWS: Small cost',
  'lesson.awsConcept': '🔴 AWS: Concept only',
  'lesson.previous': 'Previous',
  'lesson.next': 'Next',
  'lesson.notTranslated': 'Not translated yet',
  'lesson.notTranslatedDetail':
    'This lesson is not available in Bahasa Indonesia yet, so it is shown in English.',
  'lesson.showingOriginal': 'English original',
  'lesson.done': 'Done',
  'lesson.markDone': 'Mark as done',
  'lesson.onThisPage': 'On this page',
  'notes.heading': '📝 My notes',
  'notes.saved': 'Saved',
  'notes.saving': 'Saving…',
  'notes.help': 'Write the idea in your own words. Stored only in this browser.',
  'notes.placeholder': "What clicked? What's still confusing? What will you try?",
  'notes.label': 'My notes for this lesson',
  'list.done': '{done}/{total} done',
  'list.progress': '{title} progress',
  'list.comingSoon': 'Content coming soon.',
  'list.bonusPrefix': '🔥 Bonus · ',
  'list.englishOnly': 'EN',
  'list.englishOnlyTitle': 'Not translated yet — opens in English',

  // Markdown blocks
  'callout.tip': 'Tip',
  'callout.note': 'Note',
  'callout.warning': 'Warning',
  'callout.danger': 'Danger',
  'callout.revoshop': 'Find it in RevoShop',
  'callout.fastapi': 'In FastAPI…',
  'callout.bahasa': 'Dalam Bahasa',
  'code.copy': 'Copy',
  'code.copied': 'Copied ✓',
  'exercise.defaultTitle': 'Toy exercise',
  'exercise.aiAllowed': '🤖✅ AI-allowed',
  'exercise.aiAllowedTitle': 'Use AI if you like — but you must be able to explain every line.',
  'exercise.noAi': '🚫🤖 No-AI',
  'exercise.noAiTitle': 'Brain-first: solve it yourself. Use AI only afterwards, to review.',
  'exercise.folder': '📦 Folder:',
  'exercise.runChecks': '🧪 Run the checks (from the project root):',
  'exercise.pythonHelpBefore': 'No uv? Use',
  'exercise.pythonHelpInside': 'inside',
  'exercise.pythonHelpSee': '— see',
  'exercise.pythonHelpAfter':
    '. Stuck? Try the hints first; open solution/ only after a real attempt.',
  'exercise.webHelpBefore': 'First time? Run',
  'exercise.webHelpInside': 'inside',
  'exercise.webHelpAfter':
    '. Add --watch to re-run on every save. Open solution/ only after a real attempt.',
  'hints.title': 'Hints',
  'hints.show': 'Show hint {n} of {total}',
  'hints.allShown': "All hints shown. You've got this!",
  'quiz.show': 'Show answer',
  'quiz.hide': 'Hide answer',
  'part.label': 'Part {n} · ',
  'placement.title': '✅ Placement check',
  'placement.intro': 'Answer from memory — no notes, no AI. Be honest: this only helps you.',
  'placement.passed': '🎉 Passed — jump to the toy exercises and skim the rest.',
  'placement.studying': '📚 Studying this week — no problem, that is what it is for.',
  'placement.retake': 'Retake',
  'placement.pass': 'I could answer everything well',
  'placement.study': "Not yet — I'll study this week",
  'problem.defaultTitle': 'Problem',
  'problem.easy': 'easy',
  'problem.medium': 'medium',
  'problem.hard': 'hard',
  'problem.mastered': '🏆 Mastered — reviewed at every interval.',
  'problem.inQueue': '🔁 In your review queue · next review {date}',
  'problem.solved': '✅ I solved it — schedule reviews',
  'linkedin.share': 'Share your progress · {label}',
  'linkedin.copy': 'Copy template',
  'mermaid.error': 'Diagram error: {message}',
  'mermaid.drawing': 'Drawing diagram…',
  'sandpack.loading': 'Loading code editor…',
  'sandpack.defaultTitle': 'Try it in the browser',
  'sandpack.note': 'Runs in your browser · needs internet',
  'aiReview.button': '🤖 Ask AI to review',
  'aiReview.enabled': 'AI review is switched on in .env, but not built yet.',
  'aiReview.later':
    'Coming later (local Ollama first). For now, use the self-review checklist above — then compare with a friend or mentor.',

  // Search
  'search.placeholder': 'Search lessons, topics, tags…',
  'search.label': 'Search lessons',
  'search.results': 'Results',
  'search.none': 'No lessons found.',
  'search.tooShort': 'Type at least 2 characters.',

  // Dashboard & roadmap
  'dashboard.title': 'Welcome back 👋',
  'dashboard.description': "Small steps every day beat big weekends. Here's where you are.",
  'dashboard.continue': 'Continue learning',
  'dashboard.openRoadmap': 'Open the roadmap',
  'dashboard.weekPlan': "This week's plan",
  'dashboard.open': '📅 Open',
  'dashboard.reviewsDue': 'DSA reviews due',
  'dashboard.lessonsDone': 'Lessons done',
  'dashboard.newHereBefore': '📖 New here? Read',
  'dashboard.newHereAfter': 'first (10 minutes).',
  'milestones.heading': 'Job-ready milestones',
  'milestones.comingContent': 'content coming',
  'roadmap.eyebrow': 'Overview',
  'roadmap.title': 'Roadmap',
  'roadmap.description':
    'Eight modules in order, two tracks alongside them, and projects that grow with you. You can start applying for jobs at Milestone 1.',
  'roadmap.modules': 'Modules',
  'roadmap.moduleNumber': 'Module {number} · ',
  'roadmap.bonus': '🔥 Bonus',
  'roadmap.coreOutline': '📘 the bootcamp outline',
  'roadmap.comingSoon': 'coming soon',
  'roadmap.tracks': 'Parallel tracks',
  'roadmap.projects': 'Projects',

  // Module, track, project pages
  'module.eyebrow': 'Module {number} · {source}',
  'module.sourceCore': '📘 Based on the the bootcamp outline',
  'module.sourceOriginal': '🔥 Bonus module',
  'module.sourceMixed': '📘 the bootcamp outline + 🔥 bonus lessons',
  'track.eyebrow': 'Parallel track',
  'track.openReview': '🔁 Open review queue →',
  'track.startsAlongside': 'Starts alongside {week}',
  'project.main': '⭐ Main portfolio project',
  'project.standalone': '🧠 Standalone AI project',
  'project.practice': '📚 Extra practice project',
  'project.pages': 'Brief & phases',

  // Review queue
  'review.eyebrow': 'DSA for Interviews',
  'review.title': '🔁 Review Queue',
  'review.description':
    'Solve each problem again from scratch — no peeking. Remembered it? The next review moves further away ({intervals} days). Forgot? Back to 1 day.',
  'review.dueToday': 'Due today ({count})',
  'review.nothingDueBefore': 'Nothing due. 🎉 Solve new problems in the',
  'review.dsaTrack': 'DSA track',
  'review.nothingDueAfter': 'to fill your queue.',
  'review.forgot': '😵 Forgot',
  'review.remembered': '💪 Remembered',
  'review.upcoming': 'Upcoming ({count})',
  'review.mastered': '🏆 Mastered: {titles}',
  'review.reviews': 'reviews: {count}',

  // Schedule
  'schedule.eyebrow': 'Overview',
  'schedule.title': 'This Week',
  'schedule.description':
    'Your next lessons, picked in the recommended order and sized to ~18 hours. Only 🟢 Core and 🔵 Recommended lessons for your target role are included.',
  'schedule.monFri': 'Mon–Fri',
  'schedule.saturday': 'Saturday',
  'schedule.sunday': 'Sunday',
  'schedule.routineWeekday': '2 h module lesson + 1 h DSA',
  'schedule.routineSaturday': '1.5 h Architecture + 1.5 h CareerPilot',
  'schedule.routineSunday': 'Light: DSA spaced review + weekly LinkedIn post, or rest',
  'schedule.streamModule': '📘 Module lessons',
  'schedule.streamDsa': '🧩 DSA',
  'schedule.streamArchitecture': '🏛️ Architecture',
  'schedule.streamProject': '⭐ Project',
  'schedule.whenModule': 'Mon–Fri · 2 h/day',
  'schedule.whenDsa': 'Mon–Fri · 1 h/day',
  'schedule.whenSaturday': 'Saturday · 1.5 h',
  'schedule.dueOne': '🔁 1 DSA problem due for review →',
  'schedule.dueMany': '🔁 {count} DSA problems due for review →',
  'schedule.nothingPlanned': 'Nothing planned — all done here, or content is still being written.',
  'schedule.hours': '~{hours} h',
  'schedule.planned': 'Planned: ~{hours} h',

  // Settings
  'settings.eyebrow': 'App',
  'settings.title': 'Settings',
  'settings.targetRoleDescription': 'Lessons show how important they are for this role.',
  'settings.targetRoleLegend': 'Target role',
  'settings.hideNotNeeded': 'Hide lessons marked ➖ “not needed” for my target role',
  'settings.language': '🌐 Language / Bahasa',
  'settings.languageDescription':
    'Switch the app and translated lessons between English and Bahasa Indonesia. Lessons without a translation stay in English.',
  'settings.theme': 'Theme',
  'settings.backup': '💾 Progress backup',
  'settings.backupDescription':
    'Progress, notes and settings live only in this browser. Export a backup regularly — clearing browser data deletes them.',
  'settings.export': 'Export progress (.json)',
  'settings.import': 'Import backup…',
  'settings.reset': 'Reset all data',
  'settings.resetConfirm': 'Click again to delete everything',
  'settings.restored': 'Restored {count} item(s). Reloading…',
  'settings.translationProgress': '{translated} of {total} lessons translated so far.',

  // Errors
  'notFound.title': 'Page not found',
  'notFound.description': "This page doesn't exist (yet).",
  'common.backToDashboard': '← Back to dashboard',
  'error.title': 'Oops — this page crashed',
  'error.generic': 'Something went wrong.',
} as const

export type MessageKey = keyof typeof en

export const id: Record<MessageKey, string> = {
  // Layout
  'layout.skipToContent': 'Langsung ke konten',
  'topbar.openNavigation': 'Buka navigasi',
  'topbar.search': 'Cari',
  'sidebar.label': 'Navigasi handbook',
  'sidebar.close': 'Tutup navigasi',
  'sidebar.overview': 'Ringkasan',
  'sidebar.course': 'Kursus',
  'sidebar.tracks': 'Track',
  'sidebar.projects': 'Proyek',
  'sidebar.guidesAndApp': 'Panduan & Aplikasi',
  'nav.dashboard': 'Dashboard',
  'nav.roadmap': 'Roadmap',
  'nav.thisWeek': 'Minggu Ini',
  'nav.settings': 'Pengaturan',
  'tree.expand': 'Buka {label}',
  'tree.collapse': 'Tutup {label}',
  'tree.comingSoon': 'Konten segera hadir',
  'targetRole.heading': '🎯 Target peran',
  'targetRole.coreDone': 'Materi inti selesai',
  'targetRole.core': '{done}/{total} inti',

  // Theme & language
  'theme.light': 'Terang',
  'theme.dark': 'Gelap',
  'theme.system': 'Sistem',
  'theme.toggle': 'Tema: {current}. Ganti ke {next}.',
  'theme.title': 'Tema: {current}',
  'language.toggle': 'Bahasa: {current}. Ganti ke {next}.',
  'language.title': 'Bahasa / Language',

  // Roles and importance levels
  'level.core': 'Inti',
  'level.recommended': 'Disarankan',
  'level.optional': 'Opsional',
  'level.none': 'Tidak perlu',
  'role.aiFs.description': 'Gabungan Full-Stack + AI Engineer',
  'role.fs.description': 'Backend + frontend',
  'role.ai.description': 'Membangun produk dengan LLM',
  'role.be.description': 'API, database, layanan',
  'role.fe.description': 'UI, React, Next.js',
  'role.ops.description': 'CI/CD, cloud, infrastruktur',
  'roles.importance': 'Tingkat kepentingan per peran',

  // Lesson page
  'lesson.loading': 'Memuat materi…',
  'lesson.module': 'Modul {number} · {title}',
  'lesson.project': 'Proyek',
  'lesson.guide': 'Panduan',
  'lesson.sourceRef': '📘 Referensi the bootcamp · {ref}',
  'lesson.bonus': '🔥 Bonus',
  'lesson.split': '✂️ Materi dipecah',
  'lesson.studyHours': '⏱️ ~{hours} jam belajar',
  'lesson.readMinutes': '📖 {minutes} menit baca',
  'lesson.reviewed': '🕒 Ditinjau {date}',
  'lesson.awsFree': '🟢 AWS: Gratis',
  'lesson.awsSmall': '🟡 AWS: Biaya kecil',
  'lesson.awsConcept': '🔴 AWS: Konsep saja',
  'lesson.previous': 'Sebelumnya',
  'lesson.next': 'Berikutnya',
  'lesson.notTranslated': 'Belum diterjemahkan',
  'lesson.notTranslatedDetail':
    'Materi ini belum tersedia dalam Bahasa Indonesia, jadi ditampilkan dalam bahasa Inggris.',
  'lesson.showingOriginal': 'Versi asli bahasa Inggris',
  'lesson.done': 'Selesai',
  'lesson.markDone': 'Tandai selesai',
  'lesson.onThisPage': 'Di halaman ini',
  'notes.heading': '📝 Catatanku',
  'notes.saved': 'Tersimpan',
  'notes.saving': 'Menyimpan…',
  'notes.help': 'Tulis idenya dengan kata-katamu sendiri. Hanya disimpan di browser ini.',
  'notes.placeholder': 'Apa yang sudah paham? Apa yang masih bingung? Apa yang akan kamu coba?',
  'notes.label': 'Catatanku untuk materi ini',
  'list.done': '{done}/{total} selesai',
  'list.progress': 'Progres {title}',
  'list.comingSoon': 'Konten segera hadir.',
  'list.bonusPrefix': '🔥 Bonus · ',
  'list.englishOnly': 'EN',
  'list.englishOnlyTitle': 'Belum diterjemahkan — dibuka dalam bahasa Inggris',

  // Markdown blocks
  'callout.tip': 'Tips',
  'callout.note': 'Catatan',
  'callout.warning': 'Peringatan',
  'callout.danger': 'Bahaya',
  'callout.revoshop': 'Cari di RevoShop',
  'callout.fastapi': 'Di FastAPI…',
  'callout.bahasa': 'Dalam Bahasa',
  'code.copy': 'Salin',
  'code.copied': 'Tersalin ✓',
  'exercise.defaultTitle': 'Latihan kecil',
  'exercise.aiAllowed': '🤖✅ Boleh pakai AI',
  'exercise.aiAllowedTitle': 'Boleh pakai AI — tapi kamu harus bisa menjelaskan setiap barisnya.',
  'exercise.noAi': '🚫🤖 Tanpa AI',
  'exercise.noAiTitle': 'Otak dulu: kerjakan sendiri. Pakai AI hanya setelahnya, untuk review.',
  'exercise.folder': '📦 Folder:',
  'exercise.runChecks': '🧪 Jalankan pengecekan (dari root proyek):',
  'exercise.pythonHelpBefore': 'Tidak punya uv? Pakai',
  'exercise.pythonHelpInside': 'di dalam',
  'exercise.pythonHelpSee': '— lihat',
  'exercise.pythonHelpAfter':
    '. Buntu? Coba hint dulu; buka solution/ hanya setelah benar-benar mencoba.',
  'exercise.webHelpBefore': 'Pertama kali? Jalankan',
  'exercise.webHelpInside': 'di dalam',
  'exercise.webHelpAfter':
    '. Tambahkan --watch agar tes berjalan ulang setiap kali menyimpan. Buka solution/ hanya setelah benar-benar mencoba.',
  'hints.title': 'Hint',
  'hints.show': 'Tampilkan hint {n} dari {total}',
  'hints.allShown': 'Semua hint sudah ditampilkan. Kamu pasti bisa!',
  'quiz.show': 'Lihat jawaban',
  'quiz.hide': 'Sembunyikan jawaban',
  'part.label': 'Bagian {n} · ',
  'placement.title': '✅ Cek penempatan',
  'placement.intro':
    'Jawab dari ingatan — tanpa catatan, tanpa AI. Jujur saja: ini hanya untuk membantumu.',
  'placement.passed': '🎉 Lulus — langsung ke latihan kecil dan baca sekilas sisanya.',
  'placement.studying': '📚 Pelajari minggu ini — tidak apa-apa, memang untuk itu.',
  'placement.retake': 'Ulangi',
  'placement.pass': 'Aku bisa menjawab semuanya dengan baik',
  'placement.study': 'Belum — aku akan belajar minggu ini',
  'problem.defaultTitle': 'Soal',
  'problem.easy': 'mudah',
  'problem.medium': 'sedang',
  'problem.hard': 'sulit',
  'problem.mastered': '🏆 Dikuasai — sudah diulang di setiap interval.',
  'problem.inQueue': '🔁 Ada di antrean review · review berikutnya {date}',
  'problem.solved': '✅ Sudah kuselesaikan — jadwalkan review',
  'linkedin.share': 'Bagikan progresmu · {label}',
  'linkedin.copy': 'Salin template',
  'mermaid.error': 'Diagram error: {message}',
  'mermaid.drawing': 'Menggambar diagram…',
  'sandpack.loading': 'Memuat editor kode…',
  'sandpack.defaultTitle': 'Coba di browser',
  'sandpack.note': 'Berjalan di browser · butuh internet',
  'aiReview.button': '🤖 Minta AI me-review',
  'aiReview.enabled': 'Review AI sudah dinyalakan di .env, tapi belum dibuat.',
  'aiReview.later':
    'Segera hadir (Ollama lokal dulu). Untuk sekarang, pakai checklist self-review di atas — lalu bandingkan dengan teman atau mentor.',

  // Search
  'search.placeholder': 'Cari materi, topik, tag…',
  'search.label': 'Cari materi',
  'search.results': 'Hasil',
  'search.none': 'Materi tidak ditemukan.',
  'search.tooShort': 'Ketik minimal 2 karakter.',

  // Dashboard & roadmap
  'dashboard.title': 'Selamat datang kembali 👋',
  'dashboard.description':
    'Langkah kecil setiap hari lebih baik daripada belajar maraton di akhir pekan. Ini posisimu sekarang.',
  'dashboard.continue': 'Lanjutkan belajar',
  'dashboard.openRoadmap': 'Buka roadmap',
  'dashboard.weekPlan': 'Rencana minggu ini',
  'dashboard.open': '📅 Buka',
  'dashboard.reviewsDue': 'Review DSA jatuh tempo',
  'dashboard.lessonsDone': 'Materi selesai',
  'dashboard.newHereBefore': '📖 Baru di sini? Baca',
  'dashboard.newHereAfter': 'dulu (10 menit).',
  'milestones.heading': 'Milestone siap kerja',
  'milestones.comingContent': 'konten segera hadir',
  'roadmap.eyebrow': 'Ringkasan',
  'roadmap.title': 'Roadmap',
  'roadmap.description':
    'Delapan modul berurutan, dua track berjalan bersamaan, dan proyek yang tumbuh bersamamu. Kamu sudah bisa mulai melamar kerja di Milestone 1.',
  'roadmap.modules': 'Modul',
  'roadmap.moduleNumber': 'Modul {number} · ',
  'roadmap.bonus': '🔥 Bonus',
  'roadmap.coreOutline': '📘 Outline the bootcamp',
  'roadmap.comingSoon': 'segera hadir',
  'roadmap.tracks': 'Track paralel',
  'roadmap.projects': 'Proyek',

  // Module, track, project pages
  'module.eyebrow': 'Modul {number} · {source}',
  'module.sourceCore': '📘 Berdasarkan outline the bootcamp',
  'module.sourceOriginal': '🔥 Modul bonus',
  'module.sourceMixed': '📘 Outline the bootcamp + 🔥 materi bonus',
  'track.eyebrow': 'Track paralel',
  'track.openReview': '🔁 Buka antrean review →',
  'track.startsAlongside': 'Dimulai bersamaan dengan {week}',
  'project.main': '⭐ Proyek portofolio utama',
  'project.standalone': '🧠 Proyek AI mandiri',
  'project.practice': '📚 Proyek latihan tambahan',
  'project.pages': 'Brief & fase',

  // Review queue
  'review.eyebrow': 'DSA untuk Interview',
  'review.title': '🔁 Antrean Review',
  'review.description':
    'Kerjakan ulang setiap soal dari nol — tanpa mengintip. Masih ingat? Review berikutnya makin jauh ({intervals} hari). Lupa? Kembali ke 1 hari.',
  'review.dueToday': 'Jatuh tempo hari ini ({count})',
  'review.nothingDueBefore': 'Tidak ada yang jatuh tempo. 🎉 Kerjakan soal baru di',
  'review.dsaTrack': 'track DSA',
  'review.nothingDueAfter': 'untuk mengisi antreanmu.',
  'review.forgot': '😵 Lupa',
  'review.remembered': '💪 Ingat',
  'review.upcoming': 'Akan datang ({count})',
  'review.mastered': '🏆 Dikuasai: {titles}',
  'review.reviews': 'review: {count}',

  // Schedule
  'schedule.eyebrow': 'Ringkasan',
  'schedule.title': 'Minggu Ini',
  'schedule.description':
    'Materi berikutnya, dipilih sesuai urutan yang disarankan dan dibatasi ~18 jam. Hanya materi 🟢 Inti dan 🔵 Disarankan untuk target peranmu yang dimasukkan.',
  'schedule.monFri': 'Sen–Jum',
  'schedule.saturday': 'Sabtu',
  'schedule.sunday': 'Minggu',
  'schedule.routineWeekday': '2 jam materi modul + 1 jam DSA',
  'schedule.routineSaturday': '1,5 jam Architecture + 1,5 jam CareerPilot',
  'schedule.routineSunday': 'Ringan: review berkala DSA + post LinkedIn mingguan, atau istirahat',
  'schedule.streamModule': '📘 Materi modul',
  'schedule.streamDsa': '🧩 DSA',
  'schedule.streamArchitecture': '🏛️ Architecture',
  'schedule.streamProject': '⭐ Proyek',
  'schedule.whenModule': 'Sen–Jum · 2 jam/hari',
  'schedule.whenDsa': 'Sen–Jum · 1 jam/hari',
  'schedule.whenSaturday': 'Sabtu · 1,5 jam',
  'schedule.dueOne': '🔁 1 soal DSA jatuh tempo untuk review →',
  'schedule.dueMany': '🔁 {count} soal DSA jatuh tempo untuk review →',
  'schedule.nothingPlanned':
    'Tidak ada rencana — semua sudah selesai di sini, atau kontennya masih ditulis.',
  'schedule.hours': '~{hours} jam',
  'schedule.planned': 'Direncanakan: ~{hours} jam',

  // Settings
  'settings.eyebrow': 'Aplikasi',
  'settings.title': 'Pengaturan',
  'settings.targetRoleDescription': 'Setiap materi menunjukkan seberapa penting untuk peran ini.',
  'settings.targetRoleLegend': 'Target peran',
  'settings.hideNotNeeded': 'Sembunyikan materi bertanda ➖ “tidak perlu” untuk target peranku',
  'settings.language': '🌐 Bahasa / Language',
  'settings.languageDescription':
    'Ganti aplikasi dan materi yang sudah diterjemahkan antara bahasa Inggris dan Bahasa Indonesia. Materi yang belum diterjemahkan tetap dalam bahasa Inggris.',
  'settings.theme': 'Tema',
  'settings.backup': '💾 Cadangan progres',
  'settings.backupDescription':
    'Progres, catatan, dan pengaturan hanya tersimpan di browser ini. Ekspor cadangan secara rutin — menghapus data browser akan menghapus semuanya.',
  'settings.export': 'Ekspor progres (.json)',
  'settings.import': 'Impor cadangan…',
  'settings.reset': 'Hapus semua data',
  'settings.resetConfirm': 'Klik sekali lagi untuk menghapus semuanya',
  'settings.restored': '{count} item dipulihkan. Memuat ulang…',
  'settings.translationProgress': '{translated} dari {total} materi sudah diterjemahkan.',

  // Errors
  'notFound.title': 'Halaman tidak ditemukan',
  'notFound.description': 'Halaman ini tidak ada (belum ada).',
  'common.backToDashboard': '← Kembali ke dashboard',
  'error.title': 'Ups — halaman ini error',
  'error.generic': 'Terjadi kesalahan.',
}

export const MESSAGES: Record<Locale, Record<MessageKey, string>> = { en, id }

export type MessageValues = Record<string, string | number>

/** Looks up a message and fills in `{placeholders}`. Unknown placeholders stay visible. */
export function translate(locale: Locale, key: MessageKey, values?: MessageValues): string {
  const template = MESSAGES[locale][key] ?? en[key]
  if (!values) return template
  return template.replace(/\{(\w+)\}/g, (match, name: string) =>
    name in values ? String(values[name]) : match,
  )
}

export function isLocale(value: unknown): value is Locale {
  return LOCALES.includes(value as Locale)
}
