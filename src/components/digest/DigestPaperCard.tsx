import { ArrowUpRight, Play } from "lucide-react";
import { digestDate, type DigestPaper } from "../../data/digestMockData";
export default function DigestPaperCard({
  paper,
  onWatch,
}: {
  paper: DigestPaper;
  onWatch: () => void;
}) {
  return (
    <article className="digest-paper">
      <div className="digest-paper-meta">
        <span
          className="digest-score"
          aria-label={`Example relevance score: ${paper.relevanceScore}`}
        >
          {paper.relevanceScore}
        </span>
        <span>
          {paper.venue} ·{" "}
          <time dateTime={paper.publicationDate}>
            {digestDate(paper.publicationDate)}
          </time>
        </span>
      </div>
      <h3>{paper.title}</h3>
      <p className="digest-authors">{paper.authors.join(", ")}</p>
      <div className="digest-paper-actions">
        <button onClick={onWatch}>
          <Play size={13} /> Watch Shorts
        </button>
        <a href={paper.paperUrl} target="_blank" rel="noreferrer">
          Read Paper <ArrowUpRight size={13} />
        </a>
      </div>
    </article>
  );
}
