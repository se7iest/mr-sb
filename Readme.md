# MR SB // Control Terminal

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![Discord](https://img.shields.io/badge/Discord-API-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/mrontop)

Frameless PyQt6 desktop terminal for Discord channel broadcasting and group chat renaming. Custom-painted neon UI, threaded workers, real-time telemetry, and a boot sequence overlay.

## Features

- **Broadcast Protocol** — Multi-threaded message dispatcher targeting any channel ID via Discord REST v10.
- **Name Changer** — Sequential group chat renamer via REST v9 `PATCH /channels/{id}`.
- **Telemetry Dashboard** — Live counters (cast, faults, cycles) with eased numeric transitions and a 90-sample sparkline.
- **Custom Rendering** — All UI elements painted via `QPainter`: aurora backdrop, particle bursts, glass frame, neon title, rune divider, status orb.
- **Frameless Window** — Custom drag, 8-edge resize, pin-on-top toggle.
- **Auth Gate** — Local password check before the main window initializes.

## Prerequisites

- Python 3.9+
- Valid Discord user token
- Target Channel ID or Group Chat ID

## Install

```bash
git clone https://github.com/yuvi123se/mr-sb.git
cd mr-sb
pip install PyQt6 requests
