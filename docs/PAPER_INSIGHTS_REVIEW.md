# Paper insight review

English TL;DRs and seeded Q&A were revised against the cached original PDFs, focusing on the body sections listed below. This is an editorial review of the supporting methods, statements and qualifications, not an independent reproduction of every proof or experiment. PDF page numbers are one-based. No live Q&A backend is implied.

The source metadata is retained in paperInsights.json (including PDF SHA-256); source captions are intentionally omitted from the compact Explore UI.

| Paper | Supporting body sections | PDF pages |
| --- | --- | --- |
| [2610.20674](https://arxiv.org/pdf/2610.20674) | §3.2–3.3; Theorems 1 and 4; Proposition 1 | 5, 6, 7 |
| [2505.13447](https://arxiv.org/pdf/2505.13447) | §4.1; Eqs. 3–12; Algorithms 1–2 | 3, 4, 5 |
| [2512.02012](https://arxiv.org/pdf/2512.02012) | §4.1–4.2; Eqs. 9–15; Fig. 3 | 3, 4, 5 |
| [2602.04770](https://arxiv.org/pdf/2602.04770) | §3.1–3.4; Eqs. 5–14; Algorithm 1 | 2, 3, 4, 5 |
| [2511.23342](https://arxiv.org/pdf/2511.23342) | §1 and §3; Fig. 1 | 2, 3, 4 |
| [2508.07102](https://arxiv.org/pdf/2508.07102) | §5.5–7; Theorem 5.8 | 13, 14 |
| [2607.27431](https://arxiv.org/pdf/2607.27431) | §2.2–3.3; Proposition 1; Eqs. 6–12 | 4, 5, 6 |
| [2603.12366](https://arxiv.org/pdf/2603.12366) | §3.2–3.4; Propositions 3.7–3.11; Remark 3.12 | 6, 7 |
| [2605.10727](https://arxiv.org/pdf/2605.10727) | §3.1–3.4; Propositions 3.1 and 3.3 | 4, 5 |
| [2605.17244](https://arxiv.org/pdf/2605.17244) | §4.1–4.3; Eqs. 10–21 | 4, 5, 6 |
| [2606.02521](https://arxiv.org/pdf/2606.02521) | §4.1–4.2; Eqs. 9–17; Algorithm 1 | 4, 5 |
| [2606.15553](https://arxiv.org/pdf/2606.15553) | §3.2–3.3; Fig. 1; Tables 1–2; Eqs. 8–11 | 3, 4, 5 |
| [2604.04528](https://arxiv.org/pdf/2604.04528) | §III-B and §IV-A; Theorem 1; Eqs. 8–10 | 3, 4 |
| [2210.02747](https://arxiv.org/pdf/2210.02747) | §2–3.2; Theorems 1–2 | 2, 3, 4 |
| [2209.03003](https://arxiv.org/pdf/2209.03003) | §2.1; Figs. 1–2; Eq. 1 | 3, 4 |
| [2303.01469](https://arxiv.org/pdf/2303.01469) | §3–5; Algorithm 1 | 3, 4, 5 |
| [2310.14189](https://arxiv.org/pdf/2310.14189) | §2–3.2; Table 1 | 3, 4, 5 |
| [2410.12557](https://arxiv.org/pdf/2410.12557) | §3–3.1; Eqs. 3–5 | 3, 4 |
| [2503.07565](https://arxiv.org/pdf/2503.07565) | §3.1–4.1; Theorem 1; Eqs. 8–12 | 3, 4 |
| [2010.02502](https://arxiv.org/pdf/2010.02502) | §3–4; Theorem 1 | 3, 4, 5 |
| [2006.11239](https://arxiv.org/pdf/2006.11239) | §3.2–4; Eq. 14; Tables 1–2; Algorithms 1–2 | 3, 4, 5 |

Key corrections:

- Flow Map: explain existing stop-gradient/normalization training dynamics; distinguish continuous function-space convergence from finite-step divergence and conditional neighborhood convergence.
- Sinkhorn: do not generalize conditional identifiability to all empirical particle configurations; the regularized n ≥ 3 case remains open in the cited paper.
- High-order MeanFlow: theoretical results, not demonstrated large-scale sample-quality gains.
- iMF: rewriting the loss alone is equivalent; replacing the conditional JVP tangent with a learned marginal velocity is the substantive change.
- DDPM: describe the simplified noise-prediction objective and its changed weighting, not just a generic variational objective.
- Drifting MPC: cost-biased proposal generation plus best-of-M selection, not guaranteed exact optimal control.
