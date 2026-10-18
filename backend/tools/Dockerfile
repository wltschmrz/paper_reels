FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg texlive-latex-base texlive-latex-extra texlive-fonts-recommended dvisvgm \
    libpango1.0-dev libcairo2-dev pkg-config fonts-noto-cjk build-essential curl bzip2 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements*.txt ./
RUN pip install --no-cache-dir -U pip setuptools wheel && pip install --no-cache-dir -r requirements.txt
COPY . .
ENV SS_MODELS_DIR=/models
RUN bash tools/fetch_models.sh
CMD ["bash", "tools/run_golden.sh", "/jobs/golden"]
