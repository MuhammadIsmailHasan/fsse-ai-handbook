// Array methods — reference solution. Each function reads like a sentence of transformations.

export const remoteTitles = (jobs) => jobs.filter((job) => job.remote).map((job) => job.title);

export const averageSalary = (jobs) => {
  const salaries = jobs.map((job) => job.salaryMax).filter((salary) => salary !== null);
  if (salaries.length === 0) return 0;
  return Math.floor(salaries.reduce((sum, salary) => sum + salary, 0) / salaries.length);
};

export const skillCounts = (jobs) =>
  jobs
    .flatMap((job) => job.skills)
    .reduce((counts, skill) => {
      const key = skill.toLowerCase();
      return { ...counts, [key]: (counts[key] ?? 0) + 1 };
    }, {});

export const topPaying = (jobs, n) =>
  jobs
    .toSorted((a, b) => (b.salaryMax ?? -1) - (a.salaryMax ?? -1) || a.id - b.id)
    .slice(0, n);

export const jobsByCity = (jobs) =>
  Object.fromEntries(
    Object.entries(Object.groupBy(jobs, (job) => job.city)).map(([city, group]) => [city, group.map((job) => job.title)]),
  );

export const everyHasSalary = (jobs) => jobs.every((job) => job.salaryMax !== null);

export const someInCity = (jobs, city) => jobs.some((job) => job.city.toLowerCase() === city.toLowerCase());

export const uniqueSkills = (jobs) => [...new Set(jobs.flatMap((job) => job.skills.map((skill) => skill.toLowerCase())))].sort();

export const findById = (jobs, id) => jobs.find((job) => job.id === id);
