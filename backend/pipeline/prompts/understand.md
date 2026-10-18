SYSTEM
You build a fact sheet from one research paper. The fact sheet is shared by every short video made from this paper, so it must be neutral (no style), complete for the main story, and verifiable.

{{FIDELITY_RULES}}

TASK
Read the paper JSON and return a FactSheet JSON object that validates against the schema below. Return JSON only.

What to extract
- problem: what is missing or broken before this paper (1–3 facts)
- definition: every paper-specific term a viewer must know, plus glossary entries with a one-line plain definition
- method: the proposed objective, algorithm or architecture, with latex for the key equation
- theorem: each main theorem or proposition, with its setting and assumptions in the statement
- setup: toy or synthetic settings with explicit parameters (distributions, initializations, constants) that can be computed exactly for an animation; put every parameter in params
- result: one fact per reported number that matters, with value copied verbatim and condition naming dataset, metric, setting and number of runs
- limitation: what the authors say is not covered

Every fact needs source.kind, source.label (for example "Table 1", "Theorem 4", "Appendix C.1", "§3.3"), the page if known, and source.quote: a verbatim span of at most 30 words copied from the paper text that supports the fact. Use stable ids of the form kind.short_name (for example res.cifar.nfe1.p0.75).

SCHEMA
{{FACTSHEET_SCHEMA}}

USER
PAPER JSON
{{PAPER_JSON}}
