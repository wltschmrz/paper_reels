import papers from "./papers.json";

export type DigestPaper = {
  id: string;
  title: string;
  authors: string[];
  relevanceScore: number;
  publicationDate: string;
  venue: string;
  paperUrl: string;
};
export type DigestPreview = {
  subject: string;
  senderName: string;
  senderEmail: string;
  recipient: string;
  date: string;
  relevantCount: number;
  totalCount: number;
  papers: DigestPaper[];
};

// Real, source-backed catalogue metadata; scores/counts are illustrative only.
const selections = [
  ["2610.20674", 96],
  ["2602.04770", 93],
  ["2505.13447", 88],
  ["2512.02012", 87],
] as const;
export const digestMockData: DigestPreview = {
  subject: "ScholarShorts Alert Digest — 20 Oct 2026",
  senderName: "ScholarShorts",
  senderEmail: "digest@scholarshorts.example",
  recipient: "You",
  date: "2026-10-20",
  relevantCount: 68,
  totalCount: 1995,
  papers: selections.map(([id, relevanceScore]) => {
    const paper = papers.find((p) => p.id === id)!;
    return {
      id,
      relevanceScore,
      title: paper.title,
      authors: paper.authors,
      publicationDate: paper.date,
      venue: "arXiv",
      paperUrl: paper.url,
    };
  }),
};
export const digestDate = (date: string, month: "short" | "long" = "short") =>
  new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month,
    year: "numeric",
    timeZone: "UTC",
  }).format(new Date(`${date}T00:00:00Z`));
