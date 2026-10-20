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
} from "lucide-react";
import type { Short, Paper } from "../types";
import ShortCover from "./ShortCover";
import PaperQuestions from "./PaperQuestions";
import insights from "../data/paperInsights.json";
import explanationStyles from "../data/explanationStyles.json";
import { asset } from "./PaperCard";
import { useLocalState } from "../hooks/useLocalState";
const recordedStyles: Record<string, keyof typeof explanationStyles> = {
  "flowmap-reference": "geometry",
  "flowmap-v2-openai": "mathematics",
  "flowmap-v2-anthropic": "geometry",
};
export default function Explore({
  shorts,
  papers,
  initialId,
  onDetail,
}: {
  shorts: Short[];
  papers: Paper[];
  initialId?: string;
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
  const [feedback, setFeedback] = useLocalState<Record<string, string>>(
    "ss-feedback",
    {},
  );
  const layout = useRef<HTMLDivElement>(null);
  const info = useRef<HTMLElement>(null);
  const discussion = useRef<HTMLElement>(null);
  const video = useRef<HTMLVideoElement>(null);
  const lastScroll = useRef(0);
  const touchY = useRef(0);
  const short = shorts[Math.min(index, shorts.length - 1)];
  const p = papers.find((p) => p.id === short?.paperId);
  const navigate = (delta: number) => {
    setIndex((i) => Math.min(shorts.length - 1, Math.max(0, i + delta)));
  };
  useEffect(() => {
    video.current?.load();
    info.current?.scrollTo({ top: 0 });
  }, [short?.id]);
  useEffect(() => {
    const area = layout.current?.closest(".explore-main") ?? layout.current;
    if (!area) return;
    const wheel = (event: Event) => {
      const e = event as WheelEvent;
      if (
        e.ctrlKey ||
        (e.target as HTMLElement).closest(
          ".reel-info, dialog, input, textarea, select",
        )
      )
        return;
      e.preventDefault();
      if (Math.abs(e.deltaY) > 30 && Date.now() - lastScroll.current > 700) {
        setIndex((i) =>
          Math.min(shorts.length - 1, Math.max(0, i + (e.deltaY > 0 ? 1 : -1))),
        );
        lastScroll.current = Date.now();
      }
    };
    area.addEventListener("wheel", wheel, { passive: false });
    return () => area.removeEventListener("wheel", wheel);
  }, [shorts.length, Boolean(short && p)]);
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
          아직 연결된 영상이 없습니다. 새로운 설명 영상은 서비스에서 준비해
          제공합니다.
        </p>
      </div>
    );
  const toggle = (values: string[], value: string) =>
    values.includes(value)
      ? values.filter((v) => v !== value)
      : [...values, value];
  return (
    <div className="explore-layout" ref={layout}>
      <div className="reel-stage">
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
              poster={
                short.thumbnailUrl ? asset(short.thumbnailUrl) : undefined
              }
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
          onClick={() => {
            if (discussion.current && info.current) {
              info.current.scrollTo({
                top:
                  info.current.scrollTop +
                  discussion.current.getBoundingClientRect().top -
                  info.current.getBoundingClientRect().top -
                  16,
                behavior: "smooth",
              });
            }
          }}
        >
          <MessageCircle />
          <small>Ask AI</small>
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
      <aside
        className="reel-info"
        ref={info}
        tabIndex={0}
        aria-label="Behind the short"
      >
        <span className="eyebrow">BEHIND THE SHORT</span>
        <h2>{p.title}</h2>
        <div className="paper-tldr">
          <span>TL;DR</span>
          <p>
            {insights[p.id as keyof typeof insights]?.tldr ||
              "요약을 준비 중입니다. 원문 초록을 확인해 주세요."}
          </p>
        </div>
        <div className="paper-source-links">
          <button className="secondary" onClick={() => onDetail(p)}>
            Abstract details <ArrowUpRight size={14} />
          </button>
          <a
            className="secondary"
            target="_blank"
            rel="noreferrer"
            href={p.pdfUrl}
          >
            Open original PDF <ArrowUpRight size={14} />
          </a>
        </div>
        <section className="paper-qa" ref={discussion}>
          <PaperQuestions key={p.id} paperId={p.id} />
        </section>
        <hr className="perspectives-divider" />
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
              <span className="related-short-title">{s.title}</span>
              <span
                className={`perspective-badge ${s.explanationStyle || recordedStyles[s.id] || "intuition"}`}
              >
                {
                  explanationStyles[
                    s.explanationStyle || recordedStyles[s.id] || "intuition"
                  ].label
                }
              </span>
            </button>
          ))}
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
        <p className="muted feedback-storage-note">
          Ratings are saved in this browser.
        </p>
      </aside>
    </div>
  );
}
