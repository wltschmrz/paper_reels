import { useEffect, useRef, useState } from "react";
import {
  ArrowUp,
  ArrowDown,
  Bookmark,
  MessageCircle,
  Play,
  ThumbsUp,
  ThumbsDown,
  ArrowUpRight,
  Sparkles,
} from "lucide-react";
import type { Short, Paper } from "../types";
import ShortCover from "./ShortCover";
import { asset } from "./PaperCard";
import { useLocalState } from "../hooks/useLocalState";
export default function Explore({
  shorts,
  papers,
  initialId,
  onGenerate,
  onDetail,
}: {
  shorts: Short[];
  papers: Paper[];
  initialId?: string;
  onGenerate: (p: Paper) => void;
  onDetail: (p: Paper) => void;
}) {
  const [index, setIndex] = useState(
    Math.max(
      0,
      shorts.findIndex((s) => s.id === initialId),
    ),
  );
  const [reactions, setReactions] = useLocalState<Record<string, string>>(
    "ss-short-reactions",
    {},
  );
  const [saved, setSaved] = useLocalState<string[]>("ss-saved-shorts", []);
  const [following, setFollowing] = useLocalState<string[]>("ss-following", []);
  const [comments, setComments] = useLocalState<Record<string, string[]>>(
    "ss-comments",
    {},
  );
  const [feedback, setFeedback] = useLocalState<Record<string, string>>(
    "ss-feedback",
    {},
  );
  const [draft, setDraft] = useState("");
  const discussion = useRef<HTMLElement>(null);
  const video = useRef<HTMLVideoElement>(null);
  const lastScroll = useRef(0);
  const touchY = useRef(0);
  const short = shorts[Math.min(index, shorts.length - 1)];
  const p = papers.find((p) => p.id === short?.paperId);
  const navigate = (delta: number) => {
    setIndex((i) => Math.min(shorts.length - 1, Math.max(0, i + delta)));
    setDraft("");
  };
  useEffect(() => {
    video.current?.load();
    setDraft("");
  }, [short?.id]);
  if (!short || !p)
    return (
      <div className="explore-empty">
        <div className="empty-play">
          <Play size={38} />
        </div>
        <span className="eyebrow">A NEW WAY TO DISCOVER</span>
        <h2>
          Your next perspective
          <br />
          starts with a paper.
        </h2>
        <p>
          아직 연결된 영상이 없습니다. 논문에서 데모를 만들거나
          <br />
          기존 샘플 영상을 연결하면 이곳에서 탐색할 수 있습니다.
        </p>
        <button className="primary" onClick={() => onGenerate(papers[0])}>
          <Sparkles size={16} />
          Create the first perspective
        </button>
        <span className="muted">Videos stay empty until you add your own.</span>
      </div>
    );
  const toggle = (values: string[], value: string) =>
    values.includes(value)
      ? values.filter((v) => v !== value)
      : [...values, value];
  return (
    <div className="explore-layout">
      <div
        className="reel-shell"
        tabIndex={0}
        aria-label="Short 탐색: 위아래 방향키로 이동"
        onKeyDown={(e) => {
          if ((e.target as HTMLElement).tagName === "TEXTAREA") return;
          if (e.key === "ArrowDown" || e.key === "ArrowUp") {
            e.preventDefault();
            navigate(e.key === "ArrowDown" ? 1 : -1);
          }
        }}
        onWheel={(e) => {
          if (
            Math.abs(e.deltaY) > 30 &&
            Date.now() - lastScroll.current > 700
          ) {
            navigate(e.deltaY > 0 ? 1 : -1);
            lastScroll.current = Date.now();
          }
        }}
        onTouchStart={(e) => {
          touchY.current = e.touches[0].clientY;
        }}
        onTouchEnd={(e) => {
          const d = touchY.current - e.changedTouches[0].clientY;
          if (Math.abs(d) > 60) navigate(d > 0 ? 1 : -1);
        }}
      >
        {short.videoUrl ? (
          <video
            ref={video}
            controls
            playsInline
            preload="metadata"
            poster={short.thumbnailUrl ? asset(short.thumbnailUrl) : undefined}
            src={asset(short.videoUrl)}
            onError={(e) => {
              const error =
                e.currentTarget.parentElement?.querySelector(".video-error");
              error?.classList.remove("hidden");
            }}
          />
        ) : (
          <div
            className={`reel-placeholder ${short.thumbnailUrl ? "has-thumbnail" : ""}`}
          >
            {short.thumbnailUrl && <ShortCover short={short} large />}
            <div className="demo-playback-note">
              <div className="orbital">
                <Play size={38} />
              </div>
              <span className="eyebrow">DEMO PREVIEW · NO VIDEO</span>
              <h2>{short.title}</h2>
              <p>영상 파일이 아직 연결되지 않았습니다.</p>
              <span>
                {short.style} · {short.duration}s
              </span>
            </div>
          </div>
        )}
        <p className="video-error hidden">
          영상을 불러올 수 없습니다. 등록된 URL을 확인해 주세요.
        </p>
        <div className="reel-caption">
          <span className="topic">{p.topics[0]}</span>
          <h3>{p.title}</h3>
          <span>
            @{short.creator}
            {short.demo && short.creator !== "you" ? " · 가상 사용자" : ""}
          </span>
          <button
            onClick={() => setFollowing(toggle(following, short.creator))}
          >
            {following.includes(short.creator) ? "Following" : "Follow"}
          </button>
        </div>
      </div>
      <div className="reel-controls">
        <button
          className={reactions[short.id] === "like" ? "selected" : ""}
          aria-label="Short 좋아요"
          aria-pressed={reactions[short.id] === "like"}
          onClick={() =>
            setReactions({
              ...reactions,
              [short.id]: reactions[short.id] === "like" ? "" : "like",
            })
          }
        >
          <ThumbsUp />
          <small>Like</small>
        </button>
        <button
          className={reactions[short.id] === "dislike" ? "selected" : ""}
          aria-label="Short 싫어요"
          aria-pressed={reactions[short.id] === "dislike"}
          onClick={() =>
            setReactions({
              ...reactions,
              [short.id]: reactions[short.id] === "dislike" ? "" : "dislike",
            })
          }
        >
          <ThumbsDown />
          <small>Dislike</small>
        </button>
        <button
          className={saved.includes(short.id) ? "selected" : ""}
          onClick={() => setSaved(toggle(saved, short.id))}
        >
          <Bookmark />
          <small>Save</small>
        </button>
        <button
          onClick={() =>
            discussion.current?.scrollIntoView({
              behavior: "smooth",
              block: "center",
            })
          }
        >
          <MessageCircle />
          <small>{(comments[short.id] || []).length} comments</small>
        </button>
        <div className="reel-pagination">
          <button
            aria-label="이전 Short"
            disabled={index === 0}
            onClick={() => navigate(-1)}
          >
            <ArrowUp />
          </button>
          <small>
            {index + 1} / {shorts.length}
          </small>
          <button
            aria-label="다음 Short"
            disabled={index >= shorts.length - 1}
            onClick={() => navigate(1)}
          >
            <ArrowDown />
          </button>
        </div>
      </div>
      <aside className="reel-info">
        <span className="eyebrow">BEHIND THE SHORT</span>
        <h2>{p.title}</h2>
        <p>{p.abstract.slice(0, 350)}…</p>
        <button className="secondary" onClick={() => onDetail(p)}>
          Paper details <ArrowUpRight size={15} />
        </button>
        <a
          className="text-button"
          target="_blank"
          rel="noreferrer"
          href={p.pdfUrl}
        >
          Open original PDF <ArrowUpRight size={14} />
        </a>
        <hr />
        <h3>How was this explanation?</h3>
        <div className="feedback-options">
          {[
            "Easy to understand",
            "Accurate explanation",
            "Good visualization",
            "Misleading or incorrect",
            "Missing limitations",
          ].map((v) => (
            <button
              key={v}
              aria-pressed={feedback[short.id] === v}
              className={feedback[short.id] === v ? "chip active" : "chip"}
              onClick={() =>
                setFeedback({
                  ...feedback,
                  [short.id]: feedback[short.id] === v ? "" : v,
                })
              }
            >
              {v}
            </button>
          ))}
        </div>
        <p className="muted">피드백·팔로우·댓글은 이 브라우저에 저장됩니다.</p>
        <button className="generate-button" onClick={() => onGenerate(p)}>
          <Sparkles size={14} />
          Create your version
        </button>
        <h3>Same paper, another perspective</h3>
        {shorts
          .filter((s) => s.paperId === p.id && s.id !== short.id)
          .map((s) => (
            <button
              className="related-short"
              key={s.id}
              onClick={() => setIndex(shorts.findIndex((x) => x.id === s.id))}
            >
              <Play size={14} />
              {s.title}
            </button>
          ))}
        <section className="comment-box" ref={discussion}>
          <h3>
            Discussion{" "}
            <span className="muted">
              {(comments[short.id] || []).length} comments
            </span>
          </h3>
          {!(comments[short.id] || []).length && (
            <p className="discussion-empty">
              첫 의견을 남겨보세요. 현재는 영상 없는 샘플 콘텐츠입니다.
            </p>
          )}
          {(comments[short.id] || []).map((c, i) => (
            <p key={i}>
              <strong className="comment-author">@you</strong>
              {c}
            </p>
          ))}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!draft.trim()) return;
              setComments({
                ...comments,
                [short.id]: [...(comments[short.id] || []), draft.trim()],
              });
              setDraft("");
            }}
          >
            <label>
              Comment
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="원문의 근거나 타임스탬프를 함께 남겨주세요"
                maxLength={2000}
              />
            </label>
            <button className="primary" disabled={!draft.trim()}>
              Post comment
            </button>
          </form>
        </section>
      </aside>
    </div>
  );
}
