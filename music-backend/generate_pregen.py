#!/usr/bin/env python3
"""Generate pregenerated songs for the JK music playlist via MiniMax-Music3 HF Space."""
import os, time, sys, json, subprocess
from gradio_client import Client

TOK = open('/home/jonathan/.cache/huggingface/token').read().strip()
OUT = '/home/jonathan/Jpalmer95.github.io/music/pregen'
os.makedirs(OUT, exist_ok=True)

# genre -> song specs
SONGS = [
    {
        "id": "lofi-chill", "genre": "Lo-fi", "title": "Coffee & Code",
        "duration": 35.0,
        "lyrics": "[Intro]\nSoft keys, the city hums below\n[Verse]\nSteam on the window, the screen glows\nQuiet thoughts in a steady flow\n[Chorus]\nChill waves carry me slow\nCoffee and code, watch the hours go\n[Outro]\nBreathe in, let the loop take hold",
        "global": "Genre: lo-fi hip hop. BPM: 78. Key: F major. Relaxed, mellow, cozy, late-night study vibe. Warm lo-fi tape texture with vinyl crackle and soft sidechain pulse.",
        "vocal": "None - purely instrumental, but with a soft humming female voice in the chorus. Intimate, airy, close-mic.",
        "arrangement": "Mellow electric piano chords, dusty sampled drums, warm bass, gentle vinyl crackle, soft pad swells, occasional vinyl pops.",
    },
    {
        "id": "synthwave", "genre": "Synthwave", "title": "Neon Horizon",
        "duration": 35.0,
        "lyrics": "[Verse]\nCity lights on chrome and steel\nMidnight drive, the world is real\n[Chorus]\nChasing the neon horizon\nRunning where the sky is rising\n[Outro]\nInto the light, we glide",
        "global": "Genre: synthwave / retrowave. BPM: 104. Key: A minor. Retro 80s retro-futuristic, nostalgic, driving, energetic. Analog synth textures with reverb-drenched pads.",
        "vocal": "Male lead vocal, smooth retro tenor, slight chorus effect, layered harmonies in chorus.",
        "arrangement": "Pulsing analog synth bass, arpeggiated leads, gated reverb snare drums, driving kick, shimmering pad layers, tape saturation.",
    },
    {
        "id": "acoustic-pop", "genre": "Acoustic Pop", "title": "Morning Light",
        "duration": 35.0,
        "lyrics": "[Verse]\nSunrise spills across the floor\nA new day knocking at my door\n[Chorus]\nOh morning light, keep shining through\nEvery shade of gold and blue\n[Outro]\nSing it with the rising sun",
        "global": "Genre: acoustic pop. BPM: 96. Key: C major. Warm, hopeful, uplifting, feel-good. Bright and intimate with a gentle build into the chorus.",
        "vocal": "Soft female lead, close and breathy, light stacked harmonies in the chorus.",
        "arrangement": "Fingerpicked acoustic guitar, soft piano, brushed drums and upright bass entering in the chorus, warm strings.",
    },
    {
        "id": "hiphop", "genre": "Hip-Hop", "title": "Steady Flow",
        "duration": 35.0,
        "lyrics": "[Verse]\nStarted from a page and a pen\nBuilt a world up again and again\n[Chorus]\nI keep it steady, steady flow\nTurn the lights low, let the story grow\n[Outro]\nOnward, on and on",
        "global": "Genre: modern hip-hop. BPM: 92. Key: D minor. Confident, laid-back, urban, midnight grind. Clean modern production, warm 808 bass.",
        "vocal": "Male vocalist, rhythmic sing-rap flow, confident, smooth delivery.",
        "arrangement": "Deep 808 sub-bass, punchy kick, crisp hi-hats, atmospheric keys, subtle choir pads, vinyl texture.",
    },
    {
        "id": "ambient", "genre": "Ambient", "title": "Quiet Constellation",
        "duration": 35.0,
        "lyrics": "[Intro]\nSpace, stillness, drift\n[Verse]\nStars like dust across the night\n[Outro]\nFloat and fade into the light",
        "global": "Genre: ambient / downtempo. BPM: 60. Key: E major. Serene, meditative, expansive, peaceful. Cinematic and spacious with slow evolution.",
        "vocal": "None - instrumental with ethereal wordless female vocal swells.",
        "arrangement": "Slow evolving pad layers, soft piano, shimmering textures, gentle sub swells, reverb-heavy atmosphere.",
    },
    {
        "id": "jazz", "genre": "Jazz", "title": "Late Night Sip",
        "duration": 35.0,
        "lyrics": "[Verse]\nDim light and a corner seat\nBlue notes under neon heat\n[Chorus]\nSwing it slow, don't rush the beat\nLet the night be bittersweet\n[Outro]\nOne more sip, one more line",
        "global": "Genre: jazz / smooth lounge. BPM: 72. Key: Bb major. Relaxed, smoky, late-night, sophisticated. Warm analog warmth with swing feel.",
        "vocal": "Female jazz vocal, sultry, smooth, intimate phrasing.",
        "arrangement": "Upright bass, brushed drums, Rhodes piano, soft saxophone phrases, subtle brushed cymbals.",
    },
]

def gen(song, client, seed):
    print(f"[{song['id']}] submitting...", flush=True)
    job = client.submit(
        song["lyrics"], song["global"], song["vocal"], song["arrangement"],
        float(song["duration"]), 0, True, 32, 4.5, song["title"],
        api_name="/output_song",
    )
    t = time.time()
    while not job.done() and time.time() - t < 400:
        time.sleep(8)
    res = job.result()
    # res tuple: (wav_path, seed_used, stats, viz_path)
    wav = res[0]
    if not os.path.exists(wav):
        print(f"[{song['id']}] FAILED - no wav", flush=True)
        return
    mp3 = os.path.join(OUT, song["id"] + ".mp3")
    subprocess.run(["ffmpeg", "-y", "-i", wav, "-codec:a", "libmp3lame", "-q:a", "4", mp3],
                   capture_output=True)
    # copy wav too
    subprocess.run(["cp", wav, os.path.join(OUT, song["id"] + ".wav")], capture_output=True)
    print(f"[{song['id']}] OK -> {mp3} ({os.path.getsize(mp3)//1024} KB)", flush=True)

def main():
    client = Client('akhaliq/MiniMax-Music3-workflow',
                    headers={'Authorization': f'Bearer {TOK}'}, verbose=False)
    for i, s in enumerate(SONGS):
        gen(s, client, i + 1)
    print("ALL DONE", flush=True)

if __name__ == "__main__":
    main()
