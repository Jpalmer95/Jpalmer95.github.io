"""
JK Music Generator — MiniMax Music 3 orchestrator backend.

Converts friendly madlibs / mood / prompt inputs into a MiniMax Music 3
Structured Caption (Global Metadata + Vocal Details + Arrangement) plus lyrics,
then generates audio by calling the akhaliq/MiniMax-Music3-workflow HF Space.

Auth: bearer token from MUSIC_API_KEY env (Space secret).
"""
import os, io, time, uuid, base64
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, List

from gradio_client import Client

SPACE = os.environ.get("MUSIC_SPACE", "akhaliq/MiniMax-Music3-workflow")
API_KEY = os.environ.get("MUSIC_API_KEY", "")
ALLOW_ORIGIN = os.environ.get("ALLOW_ORIGIN", "*")

app = FastAPI(title="JK Music Generator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOW_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Song-Id", "X-Stats", "X-Seed", "X-Lyrics"],
)

# --- model client, lazy ---
_client = None


def _get_client():
    global _client
    if _client is None:
        hf_token = os.environ.get("HF_TOKEN")
        kwargs = {"verbose": False}
        if hf_token:
            kwargs["headers"] = {"Authorization": f"Bearer {hf_token}"}
        _client = Client(SPACE, **kwargs)
    return _client


def _check_auth(authorization: str):
    if not API_KEY:
        # allow in dev when no key set
        return
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != API_KEY:
        raise HTTPException(401, "Invalid API key")


def _ascii(s: str) -> str:
    """Make a string safe for HTTP headers (latin-1). Replace non-ascii chars."""
    if not s:
        return ""
    return s.encode("ascii", "replace").decode("ascii")


# --- request models ---
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Natural-language music description")
    lyrics: Optional[str] = Field(None, description="Optional lyrics with [Section] tags; auto-generated if omitted")
    duration: float = Field(40.0, ge=10, le=180)
    seed: int = Field(0)
    randomize_seed: bool = Field(True)
    title: str = "JK Custom Song"


class MadlibsRequest(BaseModel):
    genre: str = "pop"
    topic: str = "a sunny day"
    vibe: str = "upbeat and happy"
    cadence: str = "medium tempo, steady groove"
    instruments: Optional[str] = None
    voice: Optional[str] = None
    length_sec: float = Field(40.0, ge=10, le=180)
    randomize_seed: bool = Field(True)


class MoodRequest(BaseModel):
    mood: str = Field(..., description="A mood / feeling phrase, e.g. 'rainy nostalgia'")
    length_sec: float = Field(40.0, ge=10, le=180)
    randomize_seed: bool = Field(True)


# --- prompt builders ---
def _build_structured_caption(r: GenerateRequest):
    return r.prompt  # full structured caption already provided


def _build_madlibs_caption(r: MadlibsRequest) -> str:
    inst = r.instruments or "standard instrumentation for the genre"
    voice = r.voice or "a fitting vocal style for the genre"
    return (
        f"Genre: {r.genre}. {r.cadence.capitalize()}. {r.vibe.capitalize()} and emotionally resonant. "
        f"Vocal details: {voice}, expressive and well-mixed, with tasteful harmonies. "
        f"Arrangement: {inst}; clear structure with intro, verse, chorus, bridge, and outro; "
        f"dynamic production with clean modern mixing."
    )


def _build_mood_caption(r: MoodRequest) -> str:
    return (
        f"A song evoking the mood of: {r.mood}. "
        f"Genre chosen to best fit this feeling. Emotional, evocative, and well-produced "
        f"with a clear verse-chorus structure and expressive vocals. Dynamic arrangement "
        f"that builds and resolves beautifully."
    )


# --- lyrics builders ---
_LYRICS_TEMPLATES = {
    "pop": (
        "[Verse]\nEvery little moment leads me back to you\nColors in the sky are turning every shade of blue\n"
        "[Pre-Chorus]\nAnd I feel it rising, like a wave inside my chest\n"
        "[Chorus]\nWe light up the night, we never come down\nTurning the world all around\n"
        "Sing it loud, sing it true\nEvery heartbeat's a rhythm for you\n"
        "[Bridge]\nAnd when the morning comes, we'll still be golden\n"
        "[Outro]\nOh-oh-oh, we glow, we glow"
    ),
    "rock": (
        "[Verse]\nCrack of thunder, the road is calling me\nNo turning back from what I'm meant to be\n"
        "[Pre-Chorus]\nFeel the fire burning in my veins\n"
        "[Chorus]\nWe ride on the roar of the open sky\nHands to the wheel, we never say die\n"
        "Turn it up, let it ring\nWe are the sound, the heart, the king\n"
        "[Bridge]\nLightning in my blood, I'm never slowing down\n"
        "[Outro]\nRock and roll forever, hear the sound"
    ),
    "lofi": (
        "[Intro]\nSoft keys, the night hums low\n"
        "[Verse]\nCandle glow, a quiet room\nThoughts drift by like afternoon\n"
        "[Chorus]\nLo-fi dreams, take it slow\nLet the softest rhythm flow\n"
        "[Outro]\nBreathe in, let the loop take hold"
    ),
    "hiphop": (
        "[Verse]\nStarted from a page and a pen\nBuilt a world up again and again\nThey said no, but I went\nNow I'm counting all the wins\n"
        "[Chorus]\nI keep it steady, steady flow\nTurn the lights low, let the story grow\n"
        "No shortcuts on this road\nGrind it out, reap what you sow\n"
        "[Outro]\nOnward, on and on"
    ),
    "electronic": (
        "[Verse]\nPulse of the city, a thousand lights\nWe chase the horizon through the night\n"
        "[Chorus]\nWe are the beat, the bass, the glow\nMoving fast where the currents flow\n"
        "Higher, higher, let it grow\nElectric hearts in stereo\n"
        "[Outro]\nInto the drop, we go"
    ),
    "ambient": (
        "[Intro]\nSpace, stillness, drift\n"
        "[Verse]\nStars like dust across the night\nQuiet breath, a softer light\n"
        "[Outro]\nFloat and fade into the light"
    ),
    "jazz": (
        "[Verse]\nDim light and a corner seat\nBlue notes under neon heat\n"
        "[Chorus]\nSwing it slow, don't rush the beat\nLet the night be bittersweet\n"
        "[Outro]\nOne more sip, one more line"
    ),
    "acoustic": (
        "[Verse]\nSunrise spills across the floor\nA new day knocking at my door\n"
        "[Chorus]\nOh morning light, keep shining through\nEvery shade of gold and blue\n"
        "[Outro]\nSing it with the rising sun"
    ),
    "folk": (
        "[Verse]\nDown by the river, the willows sway\nWhistling wind on a dusty way\n"
        "[Chorus]\nCarry me home, through field and stone\nWhere the wildflowers grow, I'll never walk alone\n"
        "[Outro]\nAnd the river sings us home"
    ),
    "reggae": (
        "[Verse]\nSunshine on my shoulder, breeze in my hair\nNo more worry, no more care\n"
        "[Chorus]\nOne love, one vibe, one sound\nFeel the island lift you off the ground\n"
        "[Outro]\nEverything's irie now"
    ),
}


def _madlibs_lyrics(r: MadlibsRequest) -> str:
    genre = r.genre.lower().strip()
    if genre in _LYRICS_TEMPLATES:
        base = _LYRICS_TEMPLATES[genre]
        # sprinkle the topic into the verse for a personalized touch
        if r.topic and r.topic.strip():
            base = base.replace(
                "[Verse]",
                f"[Verse]\nAbout {r.topic.strip()}, I'll sing my song\n", 1
            )
        return base
    return (
        f"[Verse]\nEvery little thing about {r.topic}\nSets my heart and soul aglow\n"
        f"[Chorus]\n{genre.capitalize()} and {r.vibe}\nThis is the song I'm singing\n"
        f"[Outro]\nAnd the story goes on"
    )


def _mood_lyrics(r: MoodRequest) -> str:
    m = r.mood.strip()
    return (
        f"[Verse]\nIn a world of {m}, I find my way\n"
        f"Colors drift and softly sway\n"
        f"[Chorus]\nLet the feeling carry me through\n"
        f"Every shade of {m}, I'm made anew\n"
        f"[Outro]\nAnd it sings me home"
    )


# --- generation ---
def _generate(lyrics, caption, duration, randomize_seed, title):
    client = _get_client()
    job = client.submit(
        lyrics, caption, "", "",   # Vocal/arrangement are folded into caption
        float(duration), 0, bool(randomize_seed), 32, 4.5, title,
        api_name="/output_song",
    )
    t = time.time()
    while not job.done() and time.time() - t < 480:
        time.sleep(8)
    if not job.done():
        raise HTTPException(504, "Generation timed out after 8 minutes")
    res = job.result()
    wav_path, seed_used, stats, _viz = res[0], res[1], res[2], res[3]
    if not os.path.exists(wav_path):
        raise HTTPException(502, "No audio returned from generator")
    with open(wav_path, "rb") as f:
        data = f.read()
    return data, seed_used, stats


@app.get("/health")
def health():
    return {"status": "ok", "space": SPACE}


@app.post("/generate")
def generate(req: GenerateRequest, authorization: Optional[str] = Header(None)):
    _check_auth(authorization)
    caption = _build_structured_caption(req)
    lyrics = req.lyrics or _LYRICS_TEMPLATES.get(
        "pop", _LYRICS_TEMPLATES["pop"]
    )
    data, seed, stats = _generate(lyrics, caption, req.duration,
                                  req.randomize_seed, req.title)
    return Response(
        content=data,
        media_type="audio/wav",
        headers={
            "X-Song-Id": uuid.uuid4().hex[:12],
            "X-Stats": _ascii(stats),
            "X-Seed": str(seed),
            "X-Lyrics": base64.b64encode(lyrics[:2000].encode("utf-8")).decode("ascii"),
        },
    )


@app.post("/generate/madlibs")
def generate_madlibs(req: MadlibsRequest,
                     authorization: Optional[str] = Header(None)):
    _check_auth(authorization)
    caption = _build_madlibs_caption(req)
    lyrics = _madlibs_lyrics(req)
    title = f"Madlibs: {req.genre} · {req.topic[:24]}"
    data, seed, stats = _generate(lyrics, caption, req.length_sec,
                                  req.randomize_seed, title)
    return Response(
        content=data,
        media_type="audio/wav",
        headers={
            "X-Song-Id": uuid.uuid4().hex[:12],
            "X-Stats": _ascii(stats),
            "X-Seed": str(seed),
            "X-Lyrics": base64.b64encode(lyrics[:2000].encode("utf-8")).decode("ascii"),
        },
    )


@app.post("/generate/mood")
def generate_mood(req: MoodRequest, authorization: Optional[str] = Header(None)):
    _check_auth(authorization)
    caption = _build_mood_caption(req)
    lyrics = _mood_lyrics(req)
    title = f"Mood: {req.mood[:30]}"
    data, seed, stats = _generate(lyrics, caption, req.length_sec,
                                  req.randomize_seed, title)
    return Response(
        content=data,
        media_type="audio/wav",
        headers={
            "X-Song-Id": uuid.uuid4().hex[:12],
            "X-Stats": _ascii(stats),
            "X-Seed": str(seed),
            "X-Lyrics": base64.b64encode(lyrics[:2000].encode("utf-8")).decode("ascii"),
        },
    )
