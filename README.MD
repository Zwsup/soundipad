# Soundpad

A desktop soundboard application built with Python and CustomTkinter. The application allows users to drag and drop audio files into a playlist and trigger them using background global hotkeys.

## Current Features

- **Drag and Drop Support:** Add `.mp3`, `.wav`, and `.ogg` audio files directly into the playlist interface.
- **Global Hotkeys:** Trigger sounds via assigned keyboard shortcuts even when the application is minimized or running in the background.
- **Panic Stop:** Instantly halts all active audio playback by pressing the `ESC` key.
- **Dark Mode UI:** Modern dark-themed interface powered by CustomTkinter.

## Requirements

- Python 3.10+
- Required packages:
  - `customtkinter`
  - `pygame-ce`
  - `tkinterdnd2`
  - `keyboard`

## Installation

Install the dependencies:

```bash
python -m pip install customtkinter pygame-ce tkinterdnd2 keyboard