import type { Short } from "../types";
import styles from "../data/explanationStyles.json";
import { Lightbulb, MoveUpRight, Sigma } from "lucide-react";
import { asset } from "../lib/assets";
export default function ShortCover({
  short,
  large = false,
}: {
  short: Short;
  large?: boolean;
}) {
  const lens =
    short.demo && !short.videoUrl && short.explanationStyle
      ? styles[short.explanationStyle]
      : null;
  const Icon =
    short.explanationStyle === "geometry"
      ? MoveUpRight
      : short.explanationStyle === "mathematics"
        ? Sigma
        : Lightbulb;
  return (
    <div
      className={`short-cover ${large ? "large-cover" : ""} ${lens ? "styled-demo" : ""}`}
      data-explanation-style={lens ? short.explanationStyle : undefined}
      style={
        { "--cover-accent": short.accent || "#c6ff00" } as React.CSSProperties
      }
    >
      {short.thumbnailUrl && (
        <img
          className={large ? "reel-demo-thumbnail" : undefined}
          src={asset(short.thumbnailUrl)}
          alt=""
        />
      )}
      <div className="cover-top">
        {lens ? (
          <span className="cover-lens">
            <Icon size={12} />
            {lens.label}
          </span>
        ) : (
          <span>{short.demo ? "DEMO" : "SHORT"}</span>
        )}
        <span>{lens ? "DEMO" : `${Math.round(short.duration)}s`}</span>
      </div>
      <div className="cover-hook">
        <span className="cover-kicker">{short.kicker || short.style}</span>
        <strong>
          {(short.hookLines || [short.title]).map((line, i) => (
            <span key={i}>{line}</span>
          ))}
        </strong>
      </div>
      {lens && <div className="cover-lens-description">{lens.description}</div>}
      {!large && (
        <div className="cover-creator">
          <span className="cover-avatar">
            {short.creator.slice(0, 1).toUpperCase()}
          </span>
          <span>
            <b>@{short.creator}</b>
            <small>{short.demo ? "가상 크리에이터" : short.style}</small>
          </span>
        </div>
      )}
    </div>
  );
}
