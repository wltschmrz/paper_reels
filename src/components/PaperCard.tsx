import explanationStyles from "../data/explanationStyles.json";
import {
  Bookmark,
  ArrowUpRight,
  ThumbsUp,
  ThumbsDown,
  Clock,
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
  canFlip?: boolean;
  saved: boolean;
  reaction?: string;
  onSave: () => void;
  onReact: (r: string) => void;
  onDetail: () => void;
  onCollect: () => void;
  onPlay: (s: Short) => void;
  onShowShorts: () => void;
};
export default function PaperCard({
  paper: p,
  mode,
  shorts,
  canFlip = false,
  saved,
  reaction,
  onSave,
  onReact,
  onDetail,
  onCollect,
  onPlay,
  onShowShorts,
}: Props) {
  const styleOrder = ["intuition", "geometry", "mathematics"] as const;
  type Slot = { short?: Short; style?: keyof typeof explanationStyles };
  const slots: Slot[] = shorts.some((s) => s.videoUrl)
    ? shorts.map((short) => ({ short, style: undefined }))
    : [
        ...shorts
          .filter((s) => !s.explanationStyle)
          .map((short) => ({ short, style: undefined })),
        ...styleOrder.flatMap<Slot>((style) => {
          const matches = shorts.filter((s) => s.explanationStyle === style);
          return matches.length
            ? matches.map((short) => ({ short, style }))
            : [{ short: undefined, style }];
        }),
      ];
  return (
    <article className="paper-card" data-paper-id={p.id} data-mode={mode}>
      <div className="paper-main card-face" key={mode}>
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
            {slots.map(({ short: s, style }) =>
              s ? (
                <button
                  key={s.id}
                  className="short-tile"
                  aria-label={`${s.title} — @${s.creator}`}
                  onClick={() => onPlay(s)}
                >
                  <ShortCover short={s} />
                </button>
              ) : style ? (
                <div
                  key={style}
                  className="shorts-pending"
                  data-style={style}
                  aria-label={`${explanationStyles[style].label} — not produced yet`}
                >
                  <Clock size={22} />
                  <strong>{explanationStyles[style].label}</strong>
                  <span>{explanationStyles[style].description}</span>
                  <small>아직 제작되지 않았어요</small>
                </div>
              ) : null,
            )}
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
          {canFlip && (
            <button
              className="short-count"
              onClick={onShowShorts}
              aria-label={`${p.title} ${mode === "papers" ? "쇼츠 버전 보기" : "초록 보기"}`}
              aria-expanded={mode === "shorts"}
            >
              <Play size={12} />
              {mode === "papers"
                ? `쇼츠 버전 보기 · ${shorts.length}`
                : "초록 보기"}
            </button>
          )}
        </div>
      </footer>
    </article>
  );
}
