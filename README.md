# Jonathan Korstad's Portfolio

> **Live Site:** [jpalmer95.github.io](https://jpalmer95.github.io/)

A modern, dark-themed personal portfolio and professional landing page built with vanilla HTML, Tailwind CSS, and Font Awesome.

## About

This is the primary digital presence for **Jonathan Korstad** — Senior Accessibility Analyst, AI Engineer, and Founder of [Kynda Coffee](https://www.kyndacoffee.com). The site serves as a centralized hub for professional experience, featured projects, and contact information.

## Tech Stack

- **HTML5** — Semantic, accessible markup
- **Tailwind CSS** — Utility-first styling via CDN
- **Font Awesome 6.5** — Iconography
- **AOS (Animate On Scroll)** — Scroll-triggered animations
- **Google Fonts (Inter)** — Clean, modern typography

## Features

- **Responsive Design** — Mobile-first layout that scales from phone to desktop
- **Accessibility First** — High contrast ratios, keyboard-navigable, semantic landmarks
- **Dark Mode Aesthetic** — `#121212` base with accent blue (`#007bff`)
- **Sticky Navigation** — Smooth-scroll to sections
- **Project Showcase** — Featured work with external links to GitHub, Hugging Face, and live deployments
- **Social Links** — Direct connections to GitHub, LinkedIn, Hugging Face, X/Twitter, and Buy Me a Coffee

## Sections

1. **Hero** — Name, title, and primary CTAs (Projects, Resume PDF, Contact, XR)
2. **About** — Applied AI & Full-Stack generalist summary across enterprise engineering, entrepreneurship, open science, gaming/XR, PIN on Glass, A11y SnapCheck, and Hermes Agent ecosystem
3. **Technical Skills** — 6-category breakdown: AI Agents/MCP/Evals, ML/RL/Multimodal GenAI, Full-Stack & Systems Dev, Data/Cloud/Self-Hosted Infra, Sim/XR/Game Engines, and Accessibility & 0-to-1 Practice
4. **Professional Experience** — Visa, Kynda Coffee, MicroAssist
5. **Featured Projects** — SynapseJourney, MenuMetrics, ForgeDNA & HermesForge, Daggr Studio & Pipelines, AllergoScope, Harmonia, GetFreeQuotes, SuperSonic & Oracle VR, Agent Oracle, PageVoice & LVL-2-Rogue, Account-It & Doge Gumball, Lakehouse-AI / Deep RL & SFT, Kynda Infrastructure
6. **Education & Certifications** — UT Austin, Fast.ai, Texas A&M, Hugging Face Deep RL Honors
7. **Hermes Agent Ecosystem & Open-Source Skills** — `game-3d-asset-skills`, `gradio-app-development`, `synapse-learn`, `hermes-security-watch`, `suno-studio` / `harmonia-music`, `cc0-asset-index`, and upstream PRs to `NousResearch/hermes-agent`
8. **Kynda Coffee** — Business highlight with direct links
9. **Contact** — Resume, Email, LinkedIn, Support, and Phone links

## Running Locally

No build step required. Simply open `index.html` in a browser, or serve with any static file server:

```bash
# Python
python -m http.server 8000

# Node.js (npx serve)
npx serve .

# VS Code Live Server
# Right-click index.html → "Open with Live Server"
```

Then visit `http://localhost:8000`.

## Deployment

This site is automatically deployed via **GitHub Pages** from the `main` branch of this repository.

To deploy updates:
```bash
git add index.html
git commit -m "Update portfolio content"
git push origin main
```

## Projects Featured on This Site

| Project | Link | Description |
|---------|------|-------------|
| **SynapseJourney** | [Live](https://synapsejourney.org) | Open-source polymath learning & open-science platform (pgvector RAG, 3D knowledge map, BYOC router, MCP server) |
| **MenuMetrics** | [Live](https://menumetrics.org) | Gram-level recipe costing, inventory & Agent API for hospitality businesses |
| **ForgeDNA & HermesForge** | [GitHub](https://github.com/Jpalmer95/ForgeDNA) | Generative 3D asset compiler + Hermes-native Godot 4.7 editor distribution & 21-tool MCP bridge |
| **Daggr Studio & Pipelines** | [HF Space](https://huggingface.co/spaces/jkorstad/daggr-studio) | Self-healing visual Gradio 6 / `daggr` workflow studio with live-probed HF Space registry |
| **AllergoScope** | [Live](https://jpalmer95.github.io/allergoscope/) | Open-science research workbench for latex-fruit syndrome & post-harvest agrochemical handling |
| **Harmonia** | [GitHub](https://github.com/Jpalmer95/harmonia) | 6-operator FM matrix synth, symbolic math DSP VM & multiline chord studio in pure Rust |
| **GetFreeQuote** | [Live](https://getfreequote.org/) | Industry-agnostic Next.js 16 + Supabase marketplace for quotes and services |
| **SuperSonic & Oracle VR** | [Play](https://jpalmer95.github.io/SuperSonic/) | Browser WebXR flight/combat sim + Godot 4.7 OpenXR/Jolt VR physics sandbox |
| **Agent Oracle** | [GitHub](https://github.com/Jpalmer95/Agent-Oracle) | High-performance Rust data oracle with Lightning Network L402 microtransactions |
| **PageVoice & LVL-2-Rogue** | [GitHub](https://github.com/Jpalmer95/pagevoice) | Local GPU TTS / voice-cloning browser extension + unified multimodal `daggr` Space |
| **Account-It & Doge Gumball** | [GitHub](https://github.com/Jpalmer95/Account-It) | Agent-native Beancount accounting + provably fair on-chain Dogecoin CC0 asset machine |
| **Lakehouse-AI, Deep RL & SFT** | [HF](https://huggingface.co/jkorstad) | Spark/Iceberg/Kafka/pgvector lakehouse, multi-agent Deep RL (HF Honors) & SmolLM3 SFT |
| **Kynda Coffee** | [Website](https://www.kyndacoffee.com) | Specialty coffee roastery, Next.js 16 e-commerce & Hermes Agent operations automation |

## License

Personal portfolio — all rights reserved. Code is open for reference and learning.

---

**Connect:** [LinkedIn](https://linkedin.com/in/jkorstad) · [GitHub](https://github.com/Jpalmer95) · [HuggingFace](https://huggingface.co/jkorstad) · [X/Twitter](https://x.com/JonathanKorstad)
