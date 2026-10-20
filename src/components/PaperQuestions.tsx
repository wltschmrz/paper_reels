import { Bot, ArrowUpRight } from "lucide-react";
import { useState } from "react";
import { useLocalState } from "../hooks/useLocalState";
import insights from "../data/paperInsights.json";
export type PaperQuestion = { id: string; text: string };
export default function PaperQuestions({ paperId }: { paperId: string }) {
  const [questions, setQuestions] = useLocalState<
    Record<string, PaperQuestion[]>
  >("ss-paper-questions", {});
  const [draft, setDraft] = useState("");
  const insight = insights[paperId as keyof typeof insights];
  return (
    <>
      <h3>
        Ask about this paper <Bot size={16} />
      </h3>
      <p className="qa-intro">
        이해가 안 된 부분이나 더 알고 싶은 내용을 질문해 보세요. 논문을 근거로
        답하는 AI Q&A를 위한 공간입니다.
      </p>
      <p className="qa-demo-note">
        프로토타입 · 질문은 이 브라우저에만 저장됩니다. 공개 공유와 실시간 AI
        답변은 아직 연결되지 않았습니다.
      </p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (!draft.trim()) return;
          setQuestions((old) => ({
            ...old,
            [paperId]: [
              ...(old[paperId] || []),
              { id: crypto.randomUUID(), text: draft.trim() },
            ],
          }));
          setDraft("");
        }}
      >
        <label>
          Question
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="예: 이 방법이 기존 연구와 다른 점은 무엇인가요?"
            maxLength={2000}
          />
        </label>
        <button className="primary" disabled={!draft.trim()}>
          Save question
        </button>
      </form>
      <div className="qa-thread" aria-live="polite">
        {(questions[paperId] || []).map((q) => (
          <article className="qa-question" key={q.id}>
            <strong>You · 질문</strong>
            <p>{q.text}</p>
            <div className="qa-pending">
              <Bot size={14} /> AI 답변 미연결 · 질문만 저장되었습니다.
            </div>
          </article>
        ))}
      </div>
      {insight && (
        <details className="qa-example">
          <summary>논문 기반 Q&A 예시 보기</summary>
          <p>
            <strong>Q.</strong> {insight.sampleQuestion}
          </p>
          <div className="qa-answer">
            <strong>
              <Bot size={14} /> AI 작성 예시 답변
            </strong>
            <p>{insight.sampleAnswer}</p>
            <a href={insight.sourceUrl} target="_blank" rel="noreferrer">
              출처: 원문 {insight.sourceSection} <ArrowUpRight size={12} />
            </a>
            <small>
              미리 작성한 초록 기반 예시이며, 위 질문에 대한 실시간 응답이
              아닙니다.
            </small>
          </div>
        </details>
      )}
    </>
  );
}
