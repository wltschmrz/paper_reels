"""Bounded arXiv-only source ingestion; archive members are read, never extracted."""

import hashlib, io, json, re, tarfile
from pathlib import Path
import httpx
import pymupdf
from bs4 import BeautifulSoup
from ..contracts import PaperDoc, Section

ID = re.compile(r"^\d{4}\.\d{4,5}(?:v\d+)?$")


def fetch(url, limit=40_000_000):
    with httpx.stream(
        "GET",
        url,
        timeout=90,
        follow_redirects=True,
        headers={"User-Agent": "ScholarShortsResearch/0.2"},
    ) as r:
        r.raise_for_status()
        body = bytearray()
        for part in r.iter_bytes():
            body.extend(part)
            if len(body) > limit:
                raise ValueError("arXiv response exceeds size limit")
        return bytes(body)


def ingest(arxiv_id, cache: Path, pdf_limit=40_000_000):
    if not ID.fullmatch(arxiv_id):
        raise ValueError("Expected arXiv identifier, not arbitrary URL")
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / "paper.json"
    if dest.exists():
        return PaperDoc.model_validate_json(dest.read_text())
    soup = BeautifulSoup(fetch(f"https://arxiv.org/abs/{arxiv_id}"), "html.parser")
    meta = lambda n: soup.find("meta", attrs={"name": n})
    title = meta("citation_title")["content"]
    abstract = soup.select_one("blockquote.abstract").get_text(" ", strip=True)
    abstract = re.sub(r"^Abstract:\s*", "", abstract)
    # Pin the fetched revision so source/PDF and shared facts cannot silently mix revisions.
    version_link = soup.find("meta", attrs={"name": "citation_pdf_url"})
    canonical = version_link["content"].rsplit("/", 1)[-1] if version_link else arxiv_id
    versions = re.findall(re.escape(arxiv_id.split("v")[0]) + r"v\d+", str(soup))
    if "v" not in canonical and versions:
        canonical = max(versions, key=lambda v: int(v.split("v")[-1]))
    if "v" in arxiv_id:
        canonical = arxiv_id
    pdf = fetch(f"https://arxiv.org/pdf/{canonical}", limit=pdf_limit)
    (cache / "paper.pdf").write_bytes(pdf)
    with pymupdf.open(stream=pdf, filetype="pdf") as doc:
        sections = [
            Section(
                id=f"page-{i + 1}", title=f"Page {i + 1}", text=p.get_text(), page=i + 1
            )
            for i, p in enumerate(doc)
        ]
    kind = "pdf"
    try:
        source = fetch(f"https://arxiv.org/src/{canonical}", limit=20_000_000)
        with tarfile.open(fileobj=io.BytesIO(source), mode="r:*") as tar:
            total = 0
            for member in tar:
                if not member.isfile() or not member.name.endswith(".tex"):
                    continue
                total += member.size
                if total > 30_000_000:
                    raise ValueError("Expanded source too large")
                text = tar.extractfile(member).read().decode("utf-8", errors="replace")
                sections.append(
                    Section(id=f"latex-{len(sections)}", title=member.name, text=text)
                )
                kind = "latex"
    except (httpx.HTTPError, tarfile.TarError, ValueError):
        pass
    paper = PaperDoc(
        paper_id=arxiv_id.split("v")[0],
        arxiv_id=arxiv_id.split("v")[0],
        version=canonical,
        source_kind=kind,
        title=title,
        authors=[
            m["content"]
            for m in soup.find_all("meta", attrs={"name": "citation_author"})
        ],
        abstract=abstract,
        sections=sections,
    )
    dest.write_text(paper.model_dump_json(indent=2))
    return paper


def quote_errors(facts, paper):
    normalize = lambda s: re.sub(r"\s+", " ", s).strip()
    corpus = normalize(
        paper.abstract + "\n" + "\n".join(s.text for s in paper.sections)
    )
    errors = []
    if facts.paper_id != paper.paper_id:
        errors.append("paper_id does not match source")
    if len(facts.ids()) != len(facts.facts):
        errors.append("duplicate fact IDs")
    if not facts.facts:
        errors.append("fact sheet is empty")
    for fact in facts.facts:
        quote = normalize(fact.source.quote or "")
        if not quote or quote not in corpus:
            errors.append(f"{fact.id}: source.quote must occur verbatim in source")
    return errors
