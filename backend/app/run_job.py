"""Child process entrypoint; secrets are inherited only by the trusted worker."""

import sys
from .settings import keys
from . import db, service


def main(jid):
    from pipeline.runner import run

    folder = service.job_dir(jid)

    def progress(event):
        fields = {k: event[k] for k in ("stage", "progress") if k in event}
        if fields:
            db.update(jid, **fields)

    state = run(folder, keys(), on_progress=progress)
    # Runner's passed artifact is held for explicit owner review.
    status = "needs_review" if state.status == "published" else state.status
    db.update(
        jid,
        status=status,
        progress=state.progress,
        stage=state.stage,
        error=state.error,
        usage=[u.model_dump() for u in state.usage],
    )


if __name__ == "__main__":
    main(sys.argv[1])
