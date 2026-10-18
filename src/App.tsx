import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  Clapperboard,
  Compass,
  Bookmark,
  Folder,
  SlidersHorizontal,
  Search,
  Sparkles,
  ArrowUpRight,
  Plus,
  ArrowRight,
  Check,
  Clock,
  X,
  Menu,
  Layers,
  ChevronDown,
} from "lucide-react";
import papersData from "./data/papers.json";
import shortsData from "./data/shorts.json";
import type { Paper, Short, Preset, Job } from "./types";
import { useLocalState } from "./hooks/useLocalState";
import PaperCard, { asset } from "./components/PaperCard";
import Modal from "./components/Modal";
import Studio from "./components/Studio";
import BackendJobs from "./components/BackendJobs";
import { publishedShorts } from "./lib/backend";
import Explore from "./components/Explore";
const papers: Paper[] = papersData;
const stages = [
  "Reading the paper",
  "Script & storyboard",
  "Animation code",
  "Narration & rendering",
  "Validation & preview",
];
type View =
  "papers" | "shorts" | "explore" | "saved" | "collections" | "studio";
export default function App() {
  const [remoteShorts, setRemoteShorts] = useState<Short[]>([]);
  const refreshShorts = () =>
    publishedShorts()
      .then(setRemoteShorts)
      .catch(() => {});
  useEffect(() => {
    refreshShorts();
  }, []);
  const [view, setView] = useState<View>("papers");
  const [shortsPaperId, setShortsPaperId] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [topic, setTopic] = useState("All topics");
  const [sort, setSort] = useState("Curated");
  const [menu, setMenu] = useState(false);
  const [saved, setSaved] = useLocalState<string[]>("ss-bookmarks", []);
  const [reactions, setReactions] = useLocalState<Record<string, string>>(
    "ss-paper-reactions",
    {},
  );
  const [collections, setCollections] = useLocalState<Record<string, string[]>>(
    "ss-collections",
    { "Reading list": [] },
  );
  const [presets, setPresets] = useLocalState<Preset[]>("ss-presets", []);
  const [jobs, setJobs] = useLocalState<Job[]>("ss-jobs", []);
  const [interests, setInterests] = useLocalState<string[]>("ss-interests", [
    "MeanFlow",
    "Drifting",
  ]);
  const [detail, setDetail] = useState<Paper | null>(null);
  const [generate, setGenerate] = useState<Paper | null>(null);
  const [collect, setCollect] = useState<Paper | null>(null);
  const [newCollection, setNewCollection] = useState("");
  const [collectionFilter, setCollectionFilter] = useState("");
  const [showJobs, setShowJobs] = useState(false);
  const [showInterests, setShowInterests] = useState(false);
  const [activeShort, setActiveShort] = useState<string>();
  const [toast, setToast] = useState("");
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    if (!jobs.some((j) => j.status === "running")) return;
    const timer = setInterval(() => {
      const t = Date.now();
      setNow(t);
      setJobs((old) =>
        old.map((j) =>
          j.status === "running" && t - j.createdAt >= 20000
            ? { ...j, status: "ready" }
            : j,
        ),
      );
    }, 500);
    return () => clearInterval(timer);
  }, [jobs.some((j) => j.status === "running")]);
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(""), 3000);
    return () => clearTimeout(t);
  }, [toast]);
  const shorts: Short[] = useMemo(
    () => [
      ...(shortsData as Short[]),
      ...remoteShorts,
      ...jobs
        .filter((j) => j.status === "ready")
        .map((j) => ({
          id: j.id,
          paperId: j.paperId,
          creator: "you",
          title: j.preset.name,
          style: j.preset.approach,
          duration: Number(j.preset.duration),
          videoUrl: null,
          thumbnailUrl: null,
          demo: true,
        })),
    ],
    [jobs, remoteShorts],
  );
  const topics = [
    "All topics",
    ...Array.from(new Set(papers.flatMap((p) => p.topics))),
  ];
  const filtered = useMemo(() => {
    let list = papers.filter(
      (p) =>
        (!shortsPaperId || view !== "shorts" || p.id === shortsPaperId) &&
        (topic === "All topics" || p.topics.includes(topic)) &&
        `${p.title} ${p.abstract} ${p.authors.join(" ")} ${p.id}`
          .toLowerCase()
          .includes(search.toLowerCase()) &&
        (view !== "saved" || saved.includes(p.id)) &&
        (!collectionFilter ||
          (collections[collectionFilter] || []).includes(p.id)),
    );
    if (sort === "Newest")
      list = [...list].sort((a, b) => b.date.localeCompare(a.date));
    if (sort === "Oldest")
      list = [...list].sort((a, b) => a.date.localeCompare(b.date));
    if (sort === "For you")
      list = [...list].sort(
        (a, b) =>
          Number(b.topics.some((t) => interests.includes(t))) -
          Number(a.topics.some((t) => interests.includes(t))),
      );
    return list;
  }, [
    shortsPaperId,
    topic,
    search,
    view,
    saved,
    collectionFilter,
    collections,
    sort,
    interests,
  ]);
  const switchView = (v: View) => {
    setView(v);
    setShortsPaperId(null);
    setMenu(false);
    if (v !== "collections") setCollectionFilter("");
  };
  const showPaperShorts = (p: Paper) => {
    switchView("shorts");
    setShortsPaperId(p.id);
    setDetail(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
  const toggleSave = (p: Paper) => {
    setSaved((old) =>
      old.includes(p.id) ? old.filter((id) => id !== p.id) : [...old, p.id],
    );
  };
  const start = (preset: Preset) => {
    if (!generate) return;
    setJobs((old) => [
      {
        id: crypto.randomUUID(),
        paperId: generate.id,
        preset: { ...preset },
        createdAt: Date.now(),
        status: "running",
      },
      ...old,
    ]);
    setGenerate(null);
    setShowJobs(true);
  };
  const savePreset = (p: Preset) =>
    setPresets((old) => [...old.filter((x) => x.name !== p.name), { ...p }]);
  const goPlay = (s: Short) => {
    setActiveShort(s.id);
    switchView("explore");
  };
  const nav = [
    { id: "papers" as View, label: "Paper Feed", icon: BookOpen },
    { id: "shorts" as View, label: "Paper Shorts", icon: Clapperboard },
    { id: "explore" as View, label: "Explore", icon: Compass },
  ];
  return (
    <div className="app">
      <aside className={`sidebar ${menu ? "open" : ""}`}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            switchView("papers");
          }}
        >
          <span className="brand-icon">
            <BookOpen size={21} />
            <span />
          </span>
          Scholar<span>Shorts</span>
        </a>
        <div className="workspace-label">YOUR RESEARCH, REIMAGINED</div>
        <nav>
          {nav.map((n) => (
            <button
              key={n.id}
              className={view === n.id ? "nav-item active" : "nav-item"}
              onClick={() => switchView(n.id)}
            >
              <n.icon size={19} />
              {n.label}
              {n.id === "explore" && <span className="new-badge">NEW</span>}
            </button>
          ))}
        </nav>
        <div className="nav-label">YOUR LIBRARY</div>
        <nav>
          <button
            className={view === "saved" ? "nav-item active" : "nav-item"}
            onClick={() => switchView("saved")}
          >
            <Bookmark size={18} />
            Saved papers<span className="count">{saved.length}</span>
          </button>
          <button
            className={view === "collections" ? "nav-item active" : "nav-item"}
            onClick={() => switchView("collections")}
          >
            <Folder size={18} />
            Collections
          </button>
          <button
            className={view === "studio" ? "nav-item active" : "nav-item"}
            onClick={() => switchView("studio")}
          >
            <SlidersHorizontal size={18} />
            Creator Studio
          </button>
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <span className="tiny-stars">✦</span>
            <strong>
              One paper.
              <br />
              Multiple perspectives.
            </strong>
            <p>
              Find the explanation
              <br />
              that clicks for you.
            </p>
            <button onClick={() => setGenerate(papers[0])}>
              Create your first short <ArrowRight size={14} />
            </button>
          </div>
          <button
            className="user-profile"
            onClick={() => setShowInterests(true)}
          >
            <span className="avatar">Y</span>
            <span>
              <strong>Your workspace</strong>
              <small>Local demo account</small>
            </span>
            <SlidersHorizontal size={15} />
          </button>
        </div>
      </aside>
      <div className="app-body">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="mobile-menu icon-button"
              onClick={() => setMenu(!menu)}
              aria-label="메뉴 열기"
            >
              <Menu />
            </button>
            <span>Workspace</span>
            <span>/</span>
            <strong>
              {view === "saved"
                ? "Saved papers"
                : view === "collections"
                  ? "Collections"
                  : view === "studio"
                    ? "Creator Studio"
                    : nav.find((n) => n.id === view)?.label}
            </strong>
          </div>
          <div className="topbar-right">
            <span className="demo-badge">
              <span />
              Research prototype
            </span>
            <button
              className="icon-button jobs-button"
              aria-label="생성 작업 보기"
              onClick={() => setShowJobs(true)}
            >
              <Clock size={19} />
              {jobs.some((j) => j.status === "running") && <i />}
            </button>
            <button
              className="secondary header-interests"
              onClick={() => setShowInterests(true)}
            >
              <SlidersHorizontal size={15} />
              Your interests
            </button>
          </div>
        </header>
        <main className={view === "explore" ? "main explore-main" : "main"}>
          {view === "explore" ? (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">FOLLOW YOUR CURIOSITY</span>
                  <h1>
                    Explore perspectives<span>.</span>
                  </h1>
                  <p>One short. A new idea. A paper worth reading.</p>
                </div>
              </div>
              <Explore
                key={activeShort}
                shorts={shorts}
                papers={papers}
                initialId={activeShort}
                onGenerate={setGenerate}
                onDetail={setDetail}
              />
            </>
          ) : view === "studio" ? (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">MAKE RESEARCH YOUR OWN</span>
                  <h1>
                    Creator Studio<span>.</span>
                  </h1>
                  <p>
                    Shape how you explain. Save a perspective worth sharing.
                  </p>
                </div>
                <button
                  className="primary"
                  onClick={() => setGenerate(papers[0])}
                >
                  <Plus size={16} />
                  New short
                </button>
              </div>
              <div className="studio-dashboard">
                <section className="panel">
                  <h2>Saved presets</h2>
                  {presets.length ? (
                    presets.map((p, i) => (
                      <div className="preset-card" key={i}>
                        <Sparkles />
                        <div>
                          <h3>{p.name}</h3>
                          <p>
                            {p.approach} · {p.language} · {p.duration}s
                          </p>
                        </div>
                        <button
                          className="icon-button"
                          aria-label={`${p.name} 삭제`}
                          onClick={() =>
                            setPresets(presets.filter((_, n) => n !== i))
                          }
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ))
                  ) : (
                    <div className="empty-small">
                      <SlidersHorizontal size={30} />
                      <h3>Your style starts here</h3>
                      <p>
                        Generate Short에서 설명 방식을 설정하고 프리셋으로
                        저장하세요.
                      </p>
                    </div>
                  )}
                </section>
                <section className="panel">
                  <h2>Your generation activity</h2>
                  <p>
                    {jobs.filter((j) => j.status === "ready").length} demo
                    previews · {shorts.filter((s) => s.videoUrl).length}{" "}
                    connected videos
                  </p>
                  <button
                    className="secondary"
                    onClick={() => setShowJobs(true)}
                  >
                    View generation jobs <ArrowRight size={15} />
                  </button>
                  <div className="notice">
                    실제 생성 worker·API·결제는 아직 연결되지 않았습니다. 이
                    데모는 설정과 비동기 작업 UX를 검증합니다.
                  </div>
                </section>
              </div>
            </>
          ) : (
            <>
              {(view === "saved" || view === "collections") && (
                <div className="page-heading">
                  <h1>{view === "saved" ? "Saved papers" : "Collections"}</h1>
                </div>
              )}
              {view === "collections" && (
                <div className="collection-grid">
                  {Object.entries(collections).map(([name, ids]) => (
                    <button
                      key={name}
                      className={`collection-card ${collectionFilter === name ? "active" : ""}`}
                      onClick={() =>
                        setCollectionFilter(
                          collectionFilter === name ? "" : name,
                        )
                      }
                    >
                      <Folder size={22} />
                      <strong>{name}</strong>
                      <small>{ids.length} papers</small>
                    </button>
                  ))}
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      const name = newCollection.trim();
                      if (name && !collections[name]) {
                        setCollections({ ...collections, [name]: [] });
                        setNewCollection("");
                      }
                    }}
                  >
                    <label>
                      New collection
                      <input
                        value={newCollection}
                        onChange={(e) => setNewCollection(e.target.value)}
                        placeholder="Collection name"
                        maxLength={60}
                      />
                    </label>
                    <button
                      className="secondary"
                      disabled={!newCollection.trim()}
                    >
                      Create
                    </button>
                  </form>
                </div>
              )}
              <div className="feed-toolbar">
                <div className="feed-tabs">
                  <button
                    className={view !== "shorts" ? "active" : ""}
                    onClick={() =>
                      switchView(
                        view === "saved"
                          ? "saved"
                          : view === "collections"
                            ? "collections"
                            : "papers",
                      )
                    }
                  >
                    <BookOpen size={16} />
                    Papers<span>{filtered.length}</span>
                  </button>
                  <button
                    className={view === "shorts" ? "active" : ""}
                    onClick={() => switchView("shorts")}
                  >
                    <Clapperboard size={16} />
                    Paper Shorts
                  </button>
                </div>
                <label className="search-box">
                  <Search size={16} />
                  <input
                    aria-label="논문 검색"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search papers, authors, ideas…"
                  />
                  {search && (
                    <button
                      onClick={() => setSearch("")}
                      aria-label="검색어 지우기"
                    >
                      <X size={14} />
                    </button>
                  )}
                </label>
              </div>
              <div className="filter-row">
                <div className="topic-filters">
                  {topics.map((t) => (
                    <button
                      className={topic === t ? "chip active" : "chip"}
                      key={t}
                      onClick={() => setTopic(t)}
                    >
                      {t}
                    </button>
                  ))}
                </div>
                <label className="sort-label">
                  <span>Sort:</span>
                  <select
                    aria-label="논문 정렬"
                    value={sort}
                    onChange={(e) => setSort(e.target.value)}
                  >
                    <option>Curated</option>
                    <option>Newest</option>
                    <option>Oldest</option>
                    <option>For you</option>
                  </select>
                  <ChevronDown size={13} />
                </label>
              </div>
              {view === "shorts" && shortsPaperId && (
                <div className="paper-shorts-context panel">
                  <strong>이 논문의 쇼츠 버전</strong>
                  <button
                    className="text-button"
                    onClick={() => switchView("papers")}
                  >
                    초록 목록으로
                  </button>
                  <button
                    className="text-button"
                    onClick={() => setShortsPaperId(null)}
                  >
                    전체 쇼츠 목록
                  </button>
                </div>
              )}
              <div className="content-grid">
                <section className="feed-list">
                  <div className="list-caption">
                    <span>
                      {collectionFilter || "YOUR RESEARCH FEED"}{" "}
                      <span className="caption-dot">·</span> {filtered.length}{" "}
                      papers
                    </span>
                    <span>Curated collection, real research</span>
                  </div>
                  {filtered.length ? (
                    filtered.map((p) => (
                      <PaperCard
                        key={p.id}
                        paper={p}
                        mode={view === "shorts" ? "shorts" : "papers"}
                        shorts={shorts.filter((s) => s.paperId === p.id)}
                        saved={saved.includes(p.id)}
                        reaction={reactions[p.id]}
                        onSave={() => toggleSave(p)}
                        onReact={(r) =>
                          setReactions({
                            ...reactions,
                            [p.id]: reactions[p.id] === r ? "" : r,
                          })
                        }
                        onGenerate={() => setGenerate(p)}
                        onDetail={() => setDetail(p)}
                        onCollect={() => setCollect(p)}
                        onPlay={goPlay}
                        onShowShorts={() => showPaperShorts(p)}
                      />
                    ))
                  ) : (
                    <div className="empty-small panel">
                      <Search size={32} />
                      <h2>No papers here yet</h2>
                      <p>
                        검색·필터를 변경하거나 논문을 라이브러리에 저장해
                        주세요.
                      </p>
                      <button
                        className="secondary"
                        onClick={() => {
                          setSearch("");
                          setTopic("All topics");
                          setCollectionFilter("");
                          switchView("papers");
                        }}
                      >
                        Browse all papers
                      </button>
                    </div>
                  )}
                </section>
                <aside className="right-rail">
                  <section className="rail-card">
                    <span className="eyebrow">ON YOUR RADAR</span>
                    <h3>
                      A faster path
                      <br />
                      from noise to image.
                    </h3>
                    <p>
                      Explore the ideas connecting flow matching, MeanFlow, and
                      drifting models.
                    </p>
                    <div className="topic-stack">
                      {["MeanFlow", "Drifting", "Flow Matching"].map((t, i) => (
                        <button key={t} onClick={() => setTopic(t)}>
                          <span className={`topic-symbol symbol-${i}`}>
                            <Layers size={16} />
                          </span>
                          <span>
                            <strong>{t}</strong>
                            <small>
                              {
                                papers.filter((p) => p.topics.includes(t))
                                  .length
                              }{" "}
                              papers in this collection
                            </small>
                          </span>
                          <ArrowUpRight size={14} />
                        </button>
                      ))}
                    </div>
                  </section>
                  <section className="rail-card how-card">
                    <span className="eyebrow">FROM PAPER TO PERSPECTIVE</span>
                    <h3>Research, in your words.</h3>
                    {[
                      [
                        "01",
                        "Find a paper",
                        "Follow an idea that interests you.",
                      ],
                      [
                        "02",
                        "Make it your own",
                        "Choose a style, focus, and audience.",
                      ],
                      [
                        "03",
                        "Share a perspective",
                        "Help the next researcher get it.",
                      ],
                    ].map(([n, h, p]) => (
                      <div className="how-step" key={n}>
                        <span>{n}</span>
                        <div>
                          <strong>{h}</strong>
                          <p>{p}</p>
                        </div>
                      </div>
                    ))}
                    <button
                      className="text-button"
                      onClick={() => switchView("studio")}
                    >
                      Visit Creator Studio <ArrowRight size={14} />
                    </button>
                  </section>
                  <p className="rail-footer">
                    ScholarShorts · A research prototype
                    <br />
                    One paper, multiple perspectives.
                    <br />
                    <span>Metadata & PDF previews from arXiv.</span>
                  </p>
                </aside>
              </div>
            </>
          )}
        </main>
      </div>
      {detail && (
        <Modal title="Paper details" onClose={() => setDetail(null)} wide>
          <div className="detail-grid">
            <div>
              <span className="topic">{detail.topics[0]}</span>
              <h2>{detail.title}</h2>
              <p className="authors">{detail.authors.join(", ")}</p>
              <p className="muted">
                arXiv · {detail.date} · {detail.id}
              </p>
              <h3>Abstract</h3>
              <p className="abstract">{detail.abstract}</p>
              <div className="detail-actions">
                <a
                  className="secondary"
                  href={detail.pdfUrl}
                  target="_blank"
                  rel="noreferrer"
                >
                  Original PDF <ArrowUpRight size={15} />
                </a>
                <button
                  className="primary"
                  onClick={() => {
                    setGenerate(detail);
                    setDetail(null);
                  }}
                >
                  <Sparkles size={15} />
                  Generate Short
                </button>
                <button
                  className="secondary"
                  onClick={() => showPaperShorts(detail)}
                >
                  <Clapperboard size={15} /> 쇼츠 버전 보기
                </button>
              </div>
              <p className="muted">
                원문 초록 · 출처:{" "}
                <a href={detail.url} target="_blank" rel="noreferrer">
                  arXiv:{detail.id}
                </a>
              </p>
            </div>
            {detail.preview && (
              <a href={detail.pdfUrl} target="_blank" rel="noreferrer">
                <img
                  className="detail-preview"
                  src={asset(detail.preview)}
                  alt="논문 첫 페이지 원본 프리뷰"
                />
              </a>
            )}
          </div>
        </Modal>
      )}
      {generate && (
        <Modal
          title="Create your perspective"
          onClose={() => setGenerate(null)}
          wide
        >
          <Studio
            paper={generate}
            presets={presets}
            onSave={savePreset}
            onStart={start}
            onServerStarted={() => {
              setGenerate(null);
              setShowJobs(true);
            }}
          />
        </Modal>
      )}
      {collect && (
        <Modal title="Save to a collection" onClose={() => setCollect(null)}>
          <div className="modal-content">
            <p>{collect.title}</p>
            {Object.entries(collections).map(([name, ids]) => (
              <button
                className="collection-choice"
                key={name}
                onClick={() => {
                  setCollections({
                    ...collections,
                    [name]: ids.includes(collect.id)
                      ? ids.filter((id) => id !== collect.id)
                      : [...ids, collect.id],
                  });
                }}
              >
                <Folder size={18} />
                {name}
                {ids.includes(collect.id) && <Check size={17} />}
              </button>
            ))}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const name = newCollection.trim();
                if (name) {
                  setCollections({
                    ...collections,
                    [name]: Array.from(
                      new Set([...(collections[name] || []), collect.id]),
                    ),
                  });
                  setNewCollection("");
                  setToast("Collection saved");
                }
              }}
            >
              <label>
                New collection
                <input
                  value={newCollection}
                  onChange={(e) => setNewCollection(e.target.value)}
                  maxLength={60}
                  placeholder="e.g. One-step generation"
                />
              </label>
              <button className="primary" disabled={!newCollection.trim()}>
                Create & save
              </button>
            </form>
          </div>
        </Modal>
      )}
      {showJobs && (
        <Modal title="Generation activity" onClose={() => setShowJobs(false)}>
          <div className="modal-content">
            <BackendJobs onPublished={refreshShorts} />
            <div className="notice">
              Demo simulation · 실제 영상을 생성하거나 업로드하지 않습니다.
            </div>
            {!jobs.length && (
              <div className="empty-small">
                <Clock size={30} />
                <h3>No jobs yet</h3>
                <p>논문에서 Generate Short를 눌러 시작하세요.</p>
              </div>
            )}
            {jobs.map((j) => {
              const percent =
                j.status === "ready"
                  ? 100
                  : Math.min(99, Math.max(0, (now - j.createdAt) / 200));
              return (
                <div className="job" key={j.id}>
                  <span className="eyebrow">
                    {j.status === "ready"
                      ? "DEMO PREVIEW READY"
                      : j.status === "cancelled"
                        ? "CANCELLED"
                        : "DEMO IN PROGRESS"}
                  </span>
                  <h3>{papers.find((p) => p.id === j.paperId)?.title}</h3>
                  <p>
                    {j.preset.name} · {j.preset.language} · {j.preset.duration}s
                  </p>
                  {j.status === "running" && (
                    <>
                      <progress max={100} value={percent} />
                      <p>
                        {stages[Math.min(4, Math.floor(percent / 20))]} ·{" "}
                        {Math.floor(percent)}%
                      </p>
                      <button
                        className="text-button"
                        onClick={() =>
                          setJobs(
                            jobs.map((x) =>
                              x.id === j.id ? { ...x, status: "cancelled" } : x,
                            ),
                          )
                        }
                      >
                        Cancel job
                      </button>
                    </>
                  )}
                  {j.status === "ready" && (
                    <>
                      <p className="muted">
                        설정 미리보기만 준비되었습니다. 영상 파일은 비어
                        있습니다.
                      </p>
                      <button
                        className="secondary"
                        onClick={() => {
                          setShowJobs(false);
                          goPlay(shorts.find((s) => s.id === j.id)!);
                        }}
                      >
                        View demo preview <ArrowRight size={15} />
                      </button>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </Modal>
      )}
      {showInterests && (
        <Modal
          title="Your research interests"
          onClose={() => setShowInterests(false)}
        >
          <div className="modal-content">
            <p>
              관심 분야를 선택하고 정렬에서 “For you”를 선택하면 관련 논문이
              먼저 표시됩니다.
            </p>
            <div className="preset-chips">
              {topics.slice(1).map((t) => (
                <button
                  key={t}
                  className={interests.includes(t) ? "chip active" : "chip"}
                  onClick={() =>
                    setInterests(
                      interests.includes(t)
                        ? interests.filter((x) => x !== t)
                        : [...interests, t],
                    )
                  }
                >
                  {interests.includes(t) && <Check size={13} />} {t}
                </button>
              ))}
            </div>
            <button
              className="primary"
              onClick={() => {
                setSort("For you");
                setShowInterests(false);
                setToast("Research interests saved");
              }}
            >
              Save interests
            </button>
          </div>
        </Modal>
      )}
      {toast && (
        <div className="toast" role="status">
          <Check size={16} />
          {toast}
        </div>
      )}
    </div>
  );
}
