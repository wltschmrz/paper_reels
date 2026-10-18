import type { Preset, Short } from "../types";
export type ModelChoice = {
  provider: string;
  model: string;
  params?: Record<string, unknown>;
};
export type BackendConfig = {
  providers: Record<string, boolean>;
  models: ModelChoice[];
  stages: string[];
  blockers: string[];
  pricing: string;
  publication: string;
};
export type RemoteJob = {
  id: string;
  paper_id: string;
  status: string;
  stage: string | null;
  progress: number;
  error: string | null;
  usage: { input_tokens: number; output_tokens: number }[];
  preset: { name: string };
};
export async function api<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(`/api${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!r.ok) {
    const data = await r
      .json()
      .catch(() => ({ detail: "Backend unavailable" }));
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : JSON.stringify(data.detail),
    );
  }
  return r.json();
}
export function pipelinePreset(p: Preset, config: BackendConfig) {
  const selection = p.stageModels || {};
  const get = (stage: string) => {
    const match = config.models.find(
      (m) => `${m.provider}:${m.model}` === selection[stage],
    );
    return {
      ...(match ||
        config.models.find((m) => m.provider === "anthropic") ||
        config.models[0]),
      params: {},
    };
  };
  const lens = p.lens || "geometric";
  return {
    preset_id: "web-" + crypto.randomUUID(),
    name: p.name,
    creator_id: "owner",
    visibility: "private",
    style: {
      language: p.language === "English" ? "en" : "ko",
      audience:
        p.audience === "Beginner"
          ? "beginner"
          : p.audience === "Expert"
            ? "expert"
            : "grad",
      target_length_sec: Number(p.duration),
      tone:
        p.approach === "Critical Review" ? "critical_review" : "calm_visual",
      lens: {
        geometric: lens === "geometric" ? 0.7 : 0.1,
        equation: lens === "equation" ? 0.7 : 0.1,
        analogy: lens === "analogy" ? 0.7 : 0.1,
        empirical: lens === "empirical" ? 0.7 : 0.1,
      },
      narrative: {
        required_sections: p.requiredSections || [
          "problem",
          "method",
          "limitation",
        ],
        opening: "hook_question",
        ending: "takeaway",
      },
      math: {
        depth: Number(p.mathDepth ?? "1"),
        min_equation_dwell_sec: 2.5,
        color_terms: true,
      },
      voice: { pace: p.pace === "Slow" ? 1 : p.pace === "Fast" ? 1.35 : 1.22 },
      free_instruction: p.prompt.slice(0, 600),
    },
    models: {
      understand: get("understand"),
      storyboard: get("storyboard"),
      visual_code: get("visual_code"),
      visual_qa: get("visual_qa"),
      judge: get("judge"),
      tts: {
        provider: "supertonic_local",
        model: "supertonic-3-int8",
        params: { sid: 9, num_steps: 16 },
      },
      asr: {
        provider: "sensevoice_local",
        model: "sense-voice-int8-2024-07-17",
        params: {},
      },
      thumbnail: { provider: "render_frame", model: "hook_frame", params: {} },
    },
  };
}
export async function publishedShorts() {
  return api<Short[]>("/shorts");
}
