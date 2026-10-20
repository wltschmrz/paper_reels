import { useState } from "react";
import { ArrowLeft, BookOpen, Play, ArrowRight } from "lucide-react";
import type { Short } from "../types";
import Modal from "../components/Modal";
import { asset } from "../components/PaperCard";
import DigestPaperCard from "../components/digest/DigestPaperCard";
import {
  digestMockData as digest,
  digestDate,
  type DigestPaper,
} from "../data/digestMockData";
import "./digest.css";

export default function DigestPreviewPage({
  shorts,
  onDiscover,
  onPreferences,
}: {
  shorts: Short[];
  onDiscover: () => void;
  onPreferences: () => void;
}) {
  const [queue, setQueue] = useState<Short[] | null>(null);
  const [index, setIndex] = useState(0);
  const [unavailable, setUnavailable] = useState<DigestPaper | null>(null);
  const [ended, setEnded] = useState(false);
  const available = (id: string) =>
    shorts.filter((s) => s.paperId === id && s.videoUrl && !s.demo);
  const play = (items: Short[]) => {
    setIndex(0);
    setEnded(false);
    setQueue(items);
  };
  // One existing video per paper, in digest order. No placeholder enters playback.
  const playlist = digest.papers.flatMap((p) => available(p.id).slice(0, 1));
  const active = queue?.[index];
  return (
    <div className="digest-page">
      <div className="digest-page-nav">
        <a href="#" onClick={onDiscover}>
          <ArrowLeft size={16} /> Back to ScholarShorts
        </a>
        <span>
          ScholarShorts{" "}
          <span className="digest-nav-label">/ Email preview</span>
        </span>
      </div>
      <header className="digest-page-heading">
        <h1>Email Digest Preview</h1>
        <p>A preview of your personalized research digest.</p>
      </header>
      <section className="digest-envelope" aria-label="Email metadata">
        <div className="digest-subject">
          <h2>{digest.subject}</h2>
          <span className="digest-demo">Demo Preview</span>
        </div>
        <div className="digest-sender">
          <span className="digest-sender-icon">
            <BookOpen size={20} />
          </span>
          <div>
            <strong>{digest.senderName}</strong>{" "}
            <span>&lt;{digest.senderEmail}&gt;</span>
            <p>To: {digest.recipient}</p>
          </div>
          <time dateTime={digest.date}>{digestDate(digest.date, "long")}</time>
        </div>
      </section>
      <article className="digest-email" aria-label="Sample research email">
        <div className="digest-brand">
          <span className="brand-icon">
            <BookOpen size={23} />
            <span />
          </span>
          <strong>ScholarShorts</strong>
        </div>
        <section className="digest-summary">
          <h2>ScholarShorts Digest</h2>
          <time dateTime={digest.date}>{digestDate(digest.date)}</time>
          <p>
            We found <strong>{digest.relevantCount} papers</strong> relevant to
            your interests
            <br className="digest-desktop-break" /> (of{" "}
            {digest.totalCount.toLocaleString("en-US")} total).
          </p>
          <button className="digest-cta" onClick={onDiscover}>
            View Full Digest <ArrowRight size={15} />
          </button>
        </section>
        <div className="digest-content">
          <p className="digest-greeting">Dear Researcher,</p>
          <p>Here are today's most relevant papers selected for you.</p>
          <button
            className="digest-cta digest-play"
            disabled={!playlist.length}
            onClick={() => play(playlist)}
          >
            <Play size={15} fill="currentColor" /> Play the Digest
          </button>
          <p className="digest-disclosure">
            Sample digest · Scores and totals are illustrative. Papers are from
            our curated collection, not today's live recommendations. Playback
            includes {playlist.length} papers with available videos.
          </p>
          <div className="digest-papers">
            {digest.papers.map((p) => (
              <DigestPaperCard
                key={p.id}
                paper={p}
                onWatch={() => {
                  const items = available(p.id);
                  if (items.length) play(items);
                  else setUnavailable(p);
                }}
              />
            ))}
          </div>
          <div className="digest-more">
            <button className="digest-cta" onClick={onDiscover}>
              Explore More Papers <ArrowRight size={15} />
            </button>
          </div>
        </div>
        <footer className="digest-email-footer">
          <p>
            You're receiving this digest because you're interested in AI
            research.
          </p>
          <p>Personalized research discovery, powered by ScholarShorts.</p>
          <div>
            <button onClick={onDiscover}>Explore ScholarShorts</button>
            <span aria-hidden="true">·</span>
            <button onClick={onPreferences}>Manage Preferences</button>
          </div>
          <p className="digest-disclosure">
            Preview only. Preferences are saved in this browser. Email
            subscriptions and unsubscribe are not enabled; no email is sent.
          </p>
          <small>© 2026 ScholarShorts</small>
        </footer>
      </article>
      {queue && active && (
        <Modal title="Digest playback" onClose={() => setQueue(null)} wide>
          <div className="digest-player">
            <p>
              {index + 1} / {queue.length} · {active.style}
            </p>
            <h3>{digest.papers.find((p) => p.id === active.paperId)?.title}</h3>
            <video
              key={active.id}
              controls
              playsInline
              preload="metadata"
              poster={
                active.thumbnailUrl ? asset(active.thumbnailUrl) : undefined
              }
              src={asset(active.videoUrl!)}
              onEnded={() => {
                if (index + 1 < queue.length) {
                  setIndex(index + 1);
                  setEnded(false);
                } else setEnded(true);
              }}
              onLoadedData={(e) => {
                if (index > 0) void e.currentTarget.play().catch(() => {});
              }}
            />
            {ended && (
              <p role="status">You've reached the end of this selection.</p>
            )}
            <div className="digest-player-controls">
              <button
                className="secondary"
                disabled={index === 0}
                onClick={() => {
                  setIndex(index - 1);
                  setEnded(false);
                }}
              >
                Previous
              </button>
              <button
                className="secondary"
                disabled={index + 1 === queue.length}
                onClick={() => {
                  setIndex(index + 1);
                  setEnded(false);
                }}
              >
                Next video <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </Modal>
      )}
      {unavailable && (
        <Modal title="Shorts preview" onClose={() => setUnavailable(null)}>
          <div className="modal-content">
            <h3>{unavailable.title}</h3>
            <p>No playable short is available for this paper yet.</p>
            <p>
              The planned service will offer casual intuition, geometric
              explanations, and formal mathematical explanations, in 1–3 minute
              videos. These versions have not been generated for this paper.
            </p>
            <a
              className="secondary"
              href={unavailable.paperUrl}
              target="_blank"
              rel="noreferrer"
            >
              Read the original paper ↗
            </a>
          </div>
        </Modal>
      )}
    </div>
  );
}
