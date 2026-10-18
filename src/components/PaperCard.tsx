import {
  Bookmark,
  ArrowUpRight,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  Play,
  FolderPlus,
  FileText,
} from "lucide-react";
import type { Paper, Short } from "../types";
import ShortCover from "./ShortCover";
import { asset } from "../lib/assets";
export { asset } from "../lib/assets";
type Props = {
  paper: Paper;
  mode: "papers" | "shorts";
  shorts: Short[];
  saved: boolean;
  reaction?: string;
  onSave: () => void;
  onReact: (r: string) => void;
  onGenerate: () => void;
  onDetail: () => void;
  onCollect: () => void;
  onPlay: (s: Short) => void;
  onShowShorts: () => void;
};
export default function PaperCard({
  paper: p,
  mode,
  shorts,
  saved,
  reaction,
  onSave,
  onReact,
  onGenerate,
  onDetail,
  onCollect,
  onPlay,
  onShowShorts,
}: Props) {
  return (
    <article className="paper-card">
      <div className="paper-main">
        <div className="paper-meta">
          <span
            className={`topic ${p.topics[0] === "Drifting" ? "purple" : ""}`}
          >
            {p.topics[0]}
          </span>
          <span>arXiv · {p.date.slice(0, 10)}</span>
        </div>
        <button className="paper-title" onClick={onDetail}>
          {p.title}
        </button>
        <p className="authors">
          {p.authors.slice(0, 4).join(", ")}
          {p.authors.length > 4 ? ` +${p.authors.length - 4}` : ""}
        </p>
        {mode === "papers" ? (
          <>
            <p className="abstract clamp">{p.abstract}</p>
            <button className="text-button" onClick={onDetail}>
              Read abstract <ArrowUpRight size={13} />
            </button>
          </>
        ) : (
          <div className="shorts-row">
            {shorts.map((s) => (
              <button
                key={s.id}
                className="short-tile"
                aria-label={`${s.title} — @${s.creator}`}
                onClick={() => onPlay(s)}
              >
                <ShortCover short={s} />
              </button>
            ))}
            <button className="create-tile" onClick={onGenerate}>
              <Sparkles size={22} />
              <strong>
                {shorts.length
                  ? "Your perspective"
                  : "Be the first to explain it"}
              </strong>
              <span>Create a short for this paper</span>
            </button>
          </div>
        )}
      </div>
      {mode === "papers" && (
        <button
          className="paper-preview"
          onClick={onDetail}
          aria-label={`${p.title} 첫 페이지 보기`}
        >
          {p.preview ? (
            <img
              src={asset(p.preview)}
              alt={`${p.title} PDF 첫 페이지`}
              loading="lazy"
            />
          ) : (
            <FileText size={40} />
          )}
          <span>
            PDF PREVIEW <ArrowUpRight size={12} />
          </span>
        </button>
      )}
      <footer className="paper-actions">
        <div>
          <button
            className={
              reaction === "like" ? "icon-button selected" : "icon-button"
            }
            aria-label="관심 있는 논문"
            aria-pressed={reaction === "like"}
            onClick={() => onReact("like")}
          >
            <ThumbsUp size={16} />
          </button>
          <button
            className={
              reaction === "dislike" ? "icon-button selected" : "icon-button"
            }
            aria-label="관심 없는 논문"
            aria-pressed={reaction === "dislike"}
            onClick={() => onReact("dislike")}
          >
            <ThumbsDown size={16} />
          </button>
          <span className="separator" />
          <button
            className={saved ? "icon-button selected" : "icon-button"}
            aria-label={saved ? "북마크 해제" : "북마크"}
            aria-pressed={saved}
            onClick={onSave}
          >
            <Bookmark size={16} fill={saved ? "currentColor" : "none"} />
          </button>
          <button
            className="icon-button"
            aria-label="컬렉션에 저장"
            onClick={onCollect}
          >
            <FolderPlus size={17} />
          </button>
          <a
            className="text-button original-link"
            href={p.url}
            target="_blank"
            rel="noreferrer"
          >
            Original paper <ArrowUpRight size={14} />
          </a>
        </div>
        <div>
          {mode === "papers" && (
            <button
              className="short-count"
              onClick={onShowShorts}
              aria-label={`${p.title} 쇼츠 버전 보기`}
            >
              <Play size={12} />
              쇼츠 버전 보기 · {shorts.length}
            </button>
          )}
          <button className="generate-button" onClick={onGenerate}>
            <Sparkles size={14} />
            {mode === "papers" ? "Generate Short" : "Create Your Version"}
          </button>
        </div>
      </footer>
    </article>
  );
}
