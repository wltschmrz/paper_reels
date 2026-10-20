import { useEffect, useMemo, useState } from "react";
import {
  Mail,
  BookOpen,
  Clapperboard,
  Compass,
  Bookmark,
  Folder,
  SlidersHorizontal,
  Search,
  ArrowUpRight,
  Check,
  X,
  Menu,
  Layers,
  ChevronDown,
} from "lucide-react";
import papersData from "./data/papers.json";
import shortsData from "./data/shorts.json";
import type { Paper, Short } from "./types";
import { useLocalState } from "./hooks/useLocalState";
import PaperCard, { asset } from "./components/PaperCard";
import Modal from "./components/Modal";
import { publishedShorts } from "./lib/backend";
import Explore from "./components/Explore";
import DigestPreviewPage from "./pages/DigestPreviewPage";
const papers: Paper[] = papersData;
type View = "papers" | "shorts" | "explore" | "saved" | "collections";
export default function App() {
  const [digestOpen, setDigestOpen] = useState(
    window.location.hash === "#/digest-preview",
  );
  useEffect(() => {
    const sync = () => {
      setDigestOpen(window.location.hash === "#/digest-preview");
      setMenu(false);
    };
    window.addEventListener("hashchange", sync);
    return () => window.removeEventListener("hashchange", sync);
  }, []);
  const [remoteShorts, setRemoteShorts] = useState<Short[]>([]);
  const refreshShorts = () =>
    publishedShorts()
      .then(setRemoteShorts)
      .catch(() => {});
  useEffect(() => {
    refreshShorts();
  }, []);
  const [view, setView] = useState<View>("papers");
  const [flippedPapers, setFlippedPapers] = useState<string[]>([]);
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
  const [interests, setInterests] = useLocalState<string[]>("ss-interests", [
    "MeanFlow",
    "Drifting",
  ]);
  const [detail, setDetail] = useState<Paper | null>(null);
  const [collect, setCollect] = useState<Paper | null>(null);
  const [newCollection, setNewCollection] = useState("");
  const [collectionFilter, setCollectionFilter] = useState("");
  const [showInterests, setShowInterests] = useState(false);
  const [activeShort, setActiveShort] = useState<string>();
  const [toast, setToast] = useState("");
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(""), 3000);
    return () => clearTimeout(t);
  }, [toast]);
  const hiddenShortIds = new Set([
    "drifting-openai-baseline",
    "drifting-anthropic-baseline",
  ]);
  const shorts: Short[] = [...(shortsData as Short[]), ...remoteShorts].filter(
    (s) => !hiddenShortIds.has(s.id),
  );
  const topics = [
    "All topics",
    ...Array.from(new Set(papers.flatMap((p) => p.topics))),
  ];
  const filtered = useMemo(() => {
    let list = papers.filter(
      (p) =>
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
    if (window.location.hash === "#/digest-preview") window.location.hash = "";
    setDigestOpen(false);
    setView(v);
    if (v === "papers" || v === "shorts") setFlippedPapers([]);
    setMenu(false);
    if (v !== "collections") setCollectionFilter("");
  };
  const showPaperShorts = (p: Paper, forceOpen = false) => {
    if (view === "explore") switchView("papers");
    setFlippedPapers((ids) => {
      // Flipped means the opposite of this view's default presentation.
      const shouldFlip = forceOpen ? view !== "shorts" : !ids.includes(p.id);
      return shouldFlip
        ? Array.from(new Set([...ids, p.id]))
        : ids.filter((id) => id !== p.id);
    });
    setDetail(null);
  };
  const toggleSave = (p: Paper) => {
    setSaved((old) =>
      old.includes(p.id) ? old.filter((id) => id !== p.id) : [...old, p.id],
    );
  };
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
        </nav>
        <div className="sidebar-bottom">
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
      <div
        className={`app-body ${view === "explore" && !digestOpen ? "explore-workspace" : ""}`}
      >
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
              {digestOpen
                ? "Email Digest Preview"
                : view === "saved"
                  ? "Saved papers"
                  : view === "collections"
                    ? "Collections"
                    : nav.find((n) => n.id === view)?.label}
            </strong>
          </div>
          <div className="topbar-right">
            <span className="demo-badge">
              <span />
              Research prototype
            </span>
            <a
              className={`secondary header-digest${digestOpen ? " active" : ""}`}
              href="#/digest-preview"
              aria-label="Email Digest Preview"
              aria-current={digestOpen ? "page" : undefined}
              title="Email Digest Preview"
              onClick={() => {
                setMenu(false);
                window.scrollTo(0, 0);
              }}
            >
              <Mail size={15} />
              <span>Email Digest Preview</span>
            </a>
            <button
              className="secondary header-interests"
              onClick={() => setShowInterests(true)}
            >
              <SlidersHorizontal size={15} />
              Your interests
            </button>
          </div>
        </header>
        <main
          className={
            !digestOpen && view === "explore" ? "main explore-main" : "main"
          }
        >
          {digestOpen ? (
            <DigestPreviewPage
              shorts={shorts}
              onDiscover={() => switchView("papers")}
              onPreferences={() => setShowInterests(true)}
            />
          ) : view === "explore" ? (
            <>
              <div className="feed-tabs explore-tabs">
                <button onClick={() => switchView("papers")}>
                  <BookOpen size={16} /> Papers
                </button>
                <button onClick={() => switchView("shorts")}>
                  <Clapperboard size={16} /> Paper Shorts
                </button>
                <button
                  className="active"
                  onClick={() => switchView("explore")}
                >
                  <Compass size={16} /> Explore
                </button>
              </div>
              <Explore
                key={activeShort}
                shorts={shorts}
                papers={papers}
                initialId={activeShort}
                onDetail={setDetail}
              />
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
                  <button onClick={() => switchView("explore")}>
                    <Compass size={16} /> Explore
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
                        mode={
                          (view === "shorts") !== flippedPapers.includes(p.id)
                            ? "shorts"
                            : "papers"
                        }
                        canFlip
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
        <footer className="app-footer">
          <span>ScholarShorts · A research prototype</span>
          <a
            href="#/digest-preview"
            onClick={() => {
              setMenu(false);
              window.scrollTo(0, 0);
            }}
          >
            Email Digest Preview
          </a>
        </footer>
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
                  className="secondary"
                  onClick={() => showPaperShorts(detail, true)}
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
