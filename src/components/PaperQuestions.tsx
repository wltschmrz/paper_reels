import { Bot } from "lucide-react";
import { useEffect, useState } from "react";
import { useLocalState } from "../hooks/useLocalState";
import insights from "../data/paperInsights.json";
export type PaperQuestion = { id: string; text: string };
export default function PaperQuestions({ paperId }: { paperId: string }) {
  // Start the revised conversation with the curated example, clearing old test questions.
  const [questions, setQuestions] = useLocalState<
    Record<string, PaperQuestion[]>
  >("ss-paper-questions-v2", {});
  const [draft, setDraft] = useState("");
  useEffect(() => {
    try {
      localStorage.removeItem("ss-paper-questions");
    } catch {
      /* Storage may be unavailable. */
    }
  }, []);
  const insight = insights[paperId as keyof typeof insights];
  return (
    <>
      <h3>
        Discussion <Bot size={16} />
      </h3>
      <p className="qa-intro">Ask a question. Explore the paper with AI.</p>
      {insight && (
        <article className="qa-example">
          <div className="qa-question">
            <strong>{insight.sampleUser}</strong>
            <p>
              <b>Q.</b> {insight.sampleQuestion}
            </p>
          </div>
          <div className="qa-answer">
            <strong>
              <Bot size={14} /> ScholarShorts AI
            </strong>
            <p>{insight.sampleAnswer}</p>
          </div>
        </article>
      )}
      <div className="qa-thread" aria-live="polite">
        {(questions[paperId] || []).map((q) => (
          <article className="qa-question" key={q.id}>
            <strong>You</strong>
            <p>
              <b>Q.</b> {q.text}
            </p>
            <div className="qa-pending">
              <Bot size={14} /> Saved · AI replies coming soon
            </div>
          </article>
        ))}
      </div>
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
            placeholder="What would you like to understand?"
            maxLength={2000}
          />
        </label>
        <button className="primary" disabled={!draft.trim()}>
          Save question
        </button>
      </form>
    </>
  );
}
