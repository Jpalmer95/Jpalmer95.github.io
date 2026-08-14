---
title: JK Music Generator API
emoji: 🎧
colorFrom: indigo
colorTo: blue
sdk: docker
app_file: app.py
pinned: false
license: mit
short_description: AI song generation for jpalmer95.github.io
---

# JK Music Generator API

Lightweight FastAPI service that generates custom songs with **MiniMax Music 3**
via the `akhaliq/MiniMax-Music3-workflow` HF Space. Serves the interactive
playlist on jpalmer95.github.io.

## Endpoints

- `GET /health` — liveness check
- `POST /generate` — generate a song from a prompt + lyrics (or auto-lyrics)
- `POST /generate/madlibs` — generate from madlibs fields (genre, topic, vibe,
  cadence, instruments, voice, length)
- `POST /generate/mood` — generate from a mood phrase

`POST /generate` returns the generated MP3 as binary audio (content-type
`audio/mpeg`), plus an `X-Song-Id`, `X-Stats`, and `X-Seed` header.

## Auth

Protected by a bearer token (`MUSIC_API_KEY` env var, set as a Space secret).
The site sends it via `Authorization: Bearer <key>`.
