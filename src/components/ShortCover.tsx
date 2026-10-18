import type { Short } from "../types";
import { asset } from "../lib/assets";
export default function ShortCover({
  short,
  large = false,
}: {
  short: Short;
  large?: boolean;
}) {
  return (
    <div
      className={`short-cover ${large ? "large-cover" : ""}`}
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
        <span>{short.demo ? "DEMO" : "SHORT"}</span>
        <span>{short.duration}s</span>
      </div>
      <div className="cover-hook">
        <span className="cover-kicker">{short.kicker || short.style}</span>
        <strong>
          {(short.hookLines || [short.title]).map((line, i) => (
            <span key={i}>{line}</span>
          ))}
        </strong>
      </div>
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
