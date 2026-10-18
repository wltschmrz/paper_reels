import { useEffect, useState } from "react";
import { api, type RemoteJob } from "../lib/backend";
export default function BackendJobs({
  onPublished,
}: {
  onPublished: () => void;
}) {
  const [jobs, setJobs] = useState<RemoteJob[]>([]);
  const [error, setError] = useState("");
  async function refresh() {
    try {
      setJobs(await api<RemoteJob[]>("/jobs"));
      setError("");
    } catch {
      setError(
        "백엔드 연결 전입니다. 서버 실행 및 키 설정은 docs/BACKEND.md를 참고하세요.",
      );
    }
  }
  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 3000);
    return () => clearInterval(t);
  }, []);
  async function action(id: string, name: string) {
    try {
      await api(`/jobs/${id}/${name}`, {});
      await refresh();
      if (name === "publish") onPublished();
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <section className="backend-jobs">
      <h3>Server generation jobs</h3>
      {error && <p className="notice">{error}</p>}
      {!error && !jobs.length && (
        <p className="muted">아직 서버 생성 요청이 없습니다.</p>
      )}
      {jobs.map((j) => (
        <article className="job" key={j.id}>
          <span className="eyebrow">
            {j.status} · {j.stage || "waiting"}
          </span>
          <h3>
            {j.preset.name} · arXiv:{j.paper_id}
          </h3>
          <progress max={1} value={j.progress} />
          <p>
            {Math.round(j.progress * 100)}% · 실제 사용 토큰{" "}
            {j.usage
              .reduce((n, u) => n + u.input_tokens + u.output_tokens, 0)
              .toLocaleString()}
          </p>
          {j.error && <p className="notice">{j.error}</p>}
          {["queued", "running"].includes(j.status) && (
            <button
              className="secondary"
              onClick={() => action(j.id, "cancel")}
            >
              Cancel server job
            </button>
          )}
          {["failed", "cancelled"].includes(j.status) && (
            <button className="secondary" onClick={() => action(j.id, "retry")}>
              Retry server job
            </button>
          )}
          {j.status === "needs_review" && (
            <>
              <a
                className="text-button"
                href={`/api/jobs/${j.id}/preview/short.mp4`}
                target="_blank"
                rel="noreferrer"
              >
                생성 영상 검토 ↗
              </a>
              <a
                className="text-button"
                href={`/api/jobs/${j.id}/validation`}
                target="_blank"
                rel="noreferrer"
              >
                검증 보고서 ↗
              </a>
              <button
                className="secondary"
                onClick={() => action(j.id, "publish")}
              >
                Review complete · Publish
              </button>
              <p className="muted">
                필수 검증이 모두 통과한 영상만 게시됩니다.
              </p>
            </>
          )}
        </article>
      ))}
    </section>
  );
}
