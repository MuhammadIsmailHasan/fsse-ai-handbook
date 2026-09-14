"use client";
// Provided. Pretend this imports a 200 KB chart library that needs `window`.

export default function SalaryChart({ points }: { points: { label: string; value: number }[] }) {
  const max = Math.max(...points.map((p) => p.value));
  return (
    <figure aria-label="Salary chart">
      {points.map((p) => (
        <div key={p.label} style={{ width: `${(p.value / max) * 100}%` }} data-width={window.innerWidth > 0 ? "measured" : "unknown"}>
          {p.label}: Rp {p.value.toLocaleString("id-ID")}
        </div>
      ))}
    </figure>
  );
}
