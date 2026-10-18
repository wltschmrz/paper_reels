import { useState, useEffect } from "react";
import {
  Sparkles,
  Check,
  ArrowRight,
  Clock,
  SlidersHorizontal,
} from "lucide-react";
import type { Paper, Preset } from "../types";
import { api, pipelinePreset, type BackendConfig } from "../lib/backend";
export const defaultPreset: Preset = {
  name: "Visual intuition",
  audience: "Graduate Student",
  approach: "Intuition",
  language: "Korean",
  duration: "60",
  prompt:
    "Problem → Method → Results → Limitations 순서로 설명하고, 핵심 주장에 원문 페이지를 연결해 주세요.",
  model: "Default LLM pipeline",
  pace: "Normal",
  density: "Balanced",
  focus: "Visual intuition",
  lens: "geometric",
  mathDepth: "1",
  requiredSections: ["problem", "method", "limitation"],
};
export default function Studio({
  paper,
  presets,
  onSave,
  onStart,
  onServerStarted,
}: {
  paper: Paper;
  presets: Preset[];
  onSave: (p: Preset) => void;
  onStart: (p: Preset) => void;
  onServerStarted: () => void;
}) {
  const [p, setP] = useState<Preset>({ ...defaultPreset });
  const [saved, setSaved] = useState(false);
  const [config, setConfig] = useState<BackendConfig | null>(null);
  const [mode, setMode] = useState("demo");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    api<BackendConfig>("/config")
      .then(setConfig)
      .catch(() => {});
  }, []);
  const selectedProviders = config
    ? config.stages.map((stage) => {
        const value = p.stageModels?.[stage];
        return (
          config.models.find((m) => `${m.provider}:${m.model}` === value)
            ?.provider ||
          config.models.find((m) => m.provider === "anthropic")?.provider ||
          config.models[0].provider
        );
      })
    : [];
  const blocked =
    !config ||
    config.blockers.length > 0 ||
    selectedProviders.some((provider) => !config.providers[provider]);
  async function startServer() {
    if (!config || blocked || submitting) return;
    setSubmitting(true);
    setError("");
    try {
      await api(`/papers/${paper.id}/shorts`, {
        preset: pipelinePreset(p, config),
      });
      onServerStarted();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  const update = (key: keyof Preset, value: string) => {
    setP((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  };
  const field = (
    label: string,
    key: Exclude<keyof Preset, "requiredSections" | "stageModels">,
    values: string[],
  ) => (
    <label>
      {label}
      <select value={p[key]} onChange={(e) => update(key, e.target.value)}>
        {values.map((v) => (
          <option key={v}>{v}</option>
        ))}
      </select>
    </label>
  );
  return (
    <div className="studio">
      <div className="studio-paper">
        <span className="eyebrow">YOUR SOURCE PAPER</span>
        <h3>{paper.title}</h3>
        <span>arXiv:{paper.id}</span>
      </div>
      <div className="preset-chips generation-mode">
        <button
          className={mode === "demo" ? "chip active" : "chip"}
          onClick={() => setMode("demo")}
        >
          Demo simulation
        </button>
        <button
          className={mode === "server" ? "chip active" : "chip"}
          onClick={() => setMode("server")}
        >
          Real generation · my API keys
        </button>
      </div>
      <div className="notice">
        {mode === "demo"
          ? "데모 모드 · API 호출 없이 설정과 작업 흐름을 체험합니다."
          : "서버에 등록한 본인 API 키로 실제 비용이 발생합니다. 생성 결과는 검토 후 게시합니다."}
      </div>
      <h3>
        <SlidersHorizontal size={17} /> Make it your perspective
      </h3>
      <div className="preset-chips">
        {[
          defaultPreset,
          {
            ...defaultPreset,
            name: "Math deep dive",
            approach: "Mathematical",
            focus: "Equations",
          },
          {
            ...defaultPreset,
            name: "Critical review",
            approach: "Critical Review",
          },
          ...presets,
        ].map((v, i) => (
          <button
            key={i}
            className={p.name === v.name ? "chip active" : "chip"}
            onClick={() => {
              setP({ ...v });
              setSaved(false);
            }}
          >
            {v.name}
          </button>
        ))}
      </div>
      <div className="form-grid">
        {field("Target audience", "audience", [
          "Beginner",
          "Graduate Student",
          "Expert",
        ])}
        {field("Explanation approach", "approach", [
          "Intuition",
          "Mathematical",
          "Implementation",
          "Critical Review",
        ])}
        {field("Explanation lens", "lens", [
          "geometric",
          "equation",
          "analogy",
          "empirical",
        ])}
        {field("Math depth (0–3)", "mathDepth", ["0", "1", "2", "3"])}
        {field("Language", "language", ["Korean", "English"])}
        {field("Duration (seconds)", "duration", ["30", "60", "90"])}
        {field("Speaking pace", "pace", ["Slow", "Normal", "Fast"])}
        {field("Visual density", "density", ["Minimal", "Balanced", "Dense"])}
        {field("Primary focus", "focus", [
          "Visual intuition",
          "Theory",
          "Equations",
          "Experiments",
        ])}
      </div>
      <label>Required sections</label>
      <div className="preset-chips">
        {["problem", "method", "theory", "result", "limitation"].map(
          (section) => (
            <button
              key={section}
              className={
                (p.requiredSections || []).includes(section)
                  ? "chip active"
                  : "chip"
              }
              aria-pressed={(p.requiredSections || []).includes(section)}
              onClick={() =>
                setP((prev) => ({
                  ...prev,
                  requiredSections: (prev.requiredSections || []).includes(
                    section,
                  )
                    ? prev.requiredSections!.filter((s) => s !== section)
                    : [...(prev.requiredSections || []), section],
                }))
              }
            >
              {section}
            </button>
          ),
        )}
      </div>
      {mode === "server" && (
        <details className="model-config" open>
          <summary>Stage models · server configuration</summary>
          {!config ? (
            <p className="notice">
              백엔드 미연결. docs/BACKEND.md의 실행 방법을 확인하세요.
            </p>
          ) : (
            <>
              <div className="form-grid">
                {config.stages.map((stage) => (
                  <label key={stage}>
                    {stage}
                    <select
                      value={
                        p.stageModels?.[stage] ||
                        `${config.models.find((m) => m.provider === "anthropic")?.provider || config.models[0].provider}:${config.models.find((m) => m.provider === "anthropic")?.model || config.models[0].model}`
                      }
                      onChange={(e) =>
                        setP((prev) => ({
                          ...prev,
                          stageModels: {
                            ...prev.stageModels,
                            [stage]: e.target.value,
                          },
                        }))
                      }
                    >
                      {config.models.map((m) => (
                        <option
                          key={`${m.provider}:${m.model}`}
                          value={`${m.provider}:${m.model}`}
                        >
                          {m.provider} / {m.model}
                          {config.providers[m.provider] ? "" : " (key missing)"}
                        </option>
                      ))}
                    </select>
                  </label>
                ))}
              </div>
              {config.blockers.length > 0 && (
                <p className="notice">{config.blockers.join(" · ")}</p>
              )}
              <p className="muted">
                TTS: Supertonic local · ASR: SenseVoice local · Renderer: Manim
                + FFmpeg
                <br />
                API 비용:{" "}
                {config.pricing === "unconfigured"
                  ? "가격표 미설정 — 사전 비용 미확정"
                  : "실제 토큰 사용량을 기록합니다"}
              </p>
            </>
          )}
        </details>
      )}
      <label>
        Your direction
        <textarea
          rows={3}
          maxLength={600}
          value={p.prompt}
          onChange={(e) => update("prompt", e.target.value)}
        />
      </label>
      <div className="pipeline">
        <span>Paper analysis</span>
        <ArrowRight size={13} />
        <span>Script + Manim</span>
        <ArrowRight size={13} />
        <span>TTS</span>
        <ArrowRight size={13} />
        <span>FFmpeg</span>
      </div>
      <p className="muted">
        단계 순서와 검증은 고정입니다. 논문·근거는 공유하고 대본·시각화는
        프리셋별로 생성합니다.
      </p>
      {mode === "demo" && (
        <div className="cost-box">
          <div>
            <Clock size={17} />
            <span>
              실제 파이프라인 예상 약 30분
              <br />
              <small>데모는 20초 · 결과는 영상 없는 미리보기</small>
            </span>
          </div>
          <div>
            <strong>
              {p.model.startsWith("Quality")
                ? "24"
                : p.model.startsWith("Cost")
                  ? "6"
                  : "12"}{" "}
              demo credits
            </strong>
            <small>예시 비용 · 실제 견적 아님</small>
          </div>
        </div>
      )}
      {error && (
        <p className="notice" role="alert">
          {error}
        </p>
      )}
      <label>
        Preset name
        <input
          value={p.name}
          onChange={(e) => update("name", e.target.value)}
        />
      </label>
      <div className="modal-actions">
        <button
          className="secondary"
          disabled={!p.name.trim()}
          onClick={() => {
            onSave(p);
            setSaved(true);
          }}
        >
          {saved ? <Check size={15} /> : null}
          {saved ? "Preset saved" : "Save preset"}
        </button>
        {mode === "demo" ? (
          <button className="primary" onClick={() => onStart(p)}>
            <Sparkles size={16} />
            Start demo generation
          </button>
        ) : (
          <button
            className="primary"
            disabled={blocked || submitting}
            onClick={startServer}
          >
            <Sparkles size={16} />
            {submitting ? "Submitting…" : "Generate with my API keys"}
          </button>
        )}
      </div>
    </div>
  );
}
