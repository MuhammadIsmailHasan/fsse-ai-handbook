/**
 * linkedin.ts — post types and writing tips for "learning in public", in both languages.
 *
 * Teaches: `Record<Locale, …>` — add a language and TypeScript lists every place
 * that still needs its text.
 */
import type { Locale } from '../i18n/messages'

export type LinkedInPostType = 'weekly' | 'concept' | 'dsa' | 'build' | 'reflection' | 'milestone'

type PostGuide = Record<LinkedInPostType, { label: string; tips: string[] }>

export const LINKEDIN_POSTS: Record<Locale, PostGuide> = {
  en: {
    weekly: {
      label: '📣 Weekly recap',
      tips: [
        'Hook: start with one surprising thing you learned — not "This week I learned…".',
        'Keep it to 3 bullet points and one small struggle you overcame.',
        'Add a visual: a diagram, a code snippet screenshot or your progress bar.',
      ],
    },
    concept: {
      label: '💡 Explained simply',
      tips: [
        'Reuse your Part 2 "Explain it" answer — it is already written for non-programmers.',
        'One concept per post. An analogy beats a definition.',
        'End with a question to invite comments.',
      ],
    },
    dsa: {
      label: '🧩 Pattern + problem',
      tips: [
        'Name the pattern, show how you recognized it, and share the time complexity.',
        'Never paste full solutions to problems from paid platforms — describe the approach.',
      ],
    },
    build: {
      label: '🚀 Build in public',
      tips: [
        'Show, don’t tell: a GIF or short video of the feature working.',
        'Share one technical decision and why you made it (the trade-off).',
        'Link the GitHub repo — make sure the README is ready first.',
      ],
    },
    reflection: {
      label: '🎓 Module reflection',
      tips: [
        'What you built, what was hardest, what you would do differently.',
        'Be specific: numbers (tests written, endpoints, pages) make it credible.',
      ],
    },
    milestone: {
      label: '🎯 Milestone / open to work',
      tips: [
        'Summarize skills with proof: link 1–2 projects, not a long list of tools.',
        'Say clearly what roles you are looking for and where (remote / city).',
      ],
    },
  },
  id: {
    weekly: {
      label: '📣 Rekap mingguan',
      tips: [
        'Hook: buka dengan satu hal mengejutkan yang kamu pelajari — bukan "Minggu ini aku belajar…".',
        'Cukup 3 poin dan satu kesulitan kecil yang berhasil kamu atasi.',
        'Tambahkan visual: diagram, screenshot potongan kode, atau progress bar-mu.',
      ],
    },
    concept: {
      label: '💡 Penjelasan sederhana',
      tips: [
        'Pakai lagi jawaban "Explain it" dari Bagian 2 — sudah ditulis untuk non-programmer.',
        'Satu konsep per post. Analogi lebih kuat daripada definisi.',
        'Tutup dengan pertanyaan untuk mengundang komentar.',
      ],
    },
    dsa: {
      label: '🧩 Pola + soal',
      tips: [
        'Sebutkan polanya, tunjukkan bagaimana kamu mengenalinya, dan bagikan time complexity-nya.',
        'Jangan pernah menempel solusi lengkap soal dari platform berbayar — jelaskan pendekatannya saja.',
      ],
    },
    build: {
      label: '🚀 Build in public',
      tips: [
        'Tunjukkan, jangan hanya cerita: GIF atau video pendek fitur yang berjalan.',
        'Bagikan satu keputusan teknis dan alasannya (trade-off-nya).',
        'Tautkan repo GitHub — pastikan README sudah rapi dulu.',
      ],
    },
    reflection: {
      label: '🎓 Refleksi modul',
      tips: [
        'Apa yang kamu bangun, apa yang paling sulit, apa yang akan kamu lakukan berbeda.',
        'Spesifik: angka (jumlah tes, endpoint, halaman) membuatnya kredibel.',
      ],
    },
    milestone: {
      label: '🎯 Milestone / open to work',
      tips: [
        'Ringkas skill dengan bukti: tautkan 1–2 proyek, bukan daftar panjang tools.',
        'Sebutkan dengan jelas peran yang kamu cari dan di mana (remote / kota).',
      ],
    },
  },
}

export const LINKEDIN_RULES: Record<Locale, string[]> = {
  en: [
    'Rewrite the template in your own voice — recruiters notice copy-paste posts.',
    'Don’t share any paid course material you studied from (slides, lesson text, assignment briefs).',
    'Suggested hashtags: pick 3–5, e.g. #LearningInPublic #FullStack #Python #React #AIEngineering',
  ],
  id: [
    'Tulis ulang template dengan gayamu sendiri — recruiter bisa mengenali post hasil copy-paste.',
    'Jangan bagikan materi kursus berbayar yang kamu pelajari (slide, teks materi, brief tugas).',
    'Saran hashtag: pilih 3–5, misalnya #LearningInPublic #FullStack #Python #React #AIEngineering',
  ],
}
