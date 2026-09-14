// Provided.
export type Job = {
  id: number;
  title: string;
  company: string;
  logoUrl: string;
  bannerUrl: string;
  description: string;
  salaryPoints: { label: string; value: number }[];
};

export async function getJob(id: number): Promise<Job | null> {
  if (id !== 1) return null;
  return {
    id: 1,
    title: "Data Engineer",
    company: "Kopi Data",
    logoUrl: "https://cdn.careerpilot.app/logos/kopi-data.png",
    bannerUrl: "https://cdn.careerpilot.app/logos/kopi-data-banner.jpg",
    description: "Build **reliable** pipelines.\n\n- Python\n- SQL",
    salaryPoints: [
      { label: "Junior", value: 9_000_000 },
      { label: "Mid", value: 16_000_000 },
    ],
  };
}
