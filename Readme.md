# Tile Club – Match Puzzle Game

A casual memory-matching puzzle game built in Python using Pygame. Flip cards, test your visual recall, and match pairs of colorful fruits, flowers, animals, and cute objects across a clean, interactive board.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Screenshots & Demo](#screenshots--demo)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Gameplay & Controls](#gameplay--controls)
- [Asset Configuration](#asset-configuration)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)
- [Credits & Acknowledgments](#credits--acknowledgments)
- [License](#license)
- [Explore & Contribute](#explore--contribute)

---

## 🌟 Overview

**Tile Club** is an easy-to-play, visually engaging card-matching game designed to challenge memory and pattern recognition. Developed with Pygame, it features a complete interactive menu, customizable audio settings, move tracking, and built-in error handling to keep the gameplay smooth and resilient.

---

## ✨ Key Features

- 🎮 **Interactive Menus:** Navigate through clear **Play**, **Settings**, and **Exit** options.
- 🃏 **Classic Memory Puzzle:** 42 cards distributed across 21 matching pairs on the board.
- 🎨 **Custom Visuals:** Dedicated card-back graphic, distinct tile-face images, and background image support.
- 🎵 **Audio Controls:** Background music with an On/Off toggle switch.
- 🔊 **Volume Slider:** Adjust music levels directly within the in-game Settings panel.
- 📊 **Progress Tracking:** Live move counter and matched-pair progress indicators.
- 🔄 **Restart Option:** Quickly reset and reshuffle the board at any point during gameplay.
- 🏆 **Win Detection:** Automatically recognizes when all 21 pairs have been uncovered.
- 🛠️ **Error Handling:** Safe fallbacks when image assets or audio systems are unavailable.

---

## 📸 Screenshots & Demo

### Gameplay Preview

<![alt text](Assets/extra_file/Game_Play.gif)>

### *Menu 🎮*

![Menu](Assets/ScreenShots/menu_game.png)

---

### *Settings Panel*

![Settings Panel](Assets/ScreenShots/Setting_Menu.png)

---

### *Game Play*

![Game Play](Assets/ScreenShots/play_game.png)

---

## 💻 Technology Stack

- **Language:** Python
- **Game Engine:** [Pygame](https://www.pygame.org/)
- **Standard Libraries:** `os`, `random`

---

## 📂 Project Structure

```text
The-Club-PyGame/
├── Main_code.py
├── README.md
└── assets/
    ├── images/
    │   └── background.png
    ├── tiles/
    │   ├── card_back.png
    │   └── tile_*.png
    ├── music/
    │   └── background.mp3
    ├── buttons/
    │   ├── button_restart.png
    │   ├── button_shuffle.png
    │   └── background.mp3
    └── ScreenShots/
        ├── menu_game.png
        ├── play_game.png
        └── Setting_Menu.png
```

---

## 🚀 Installation & Setup

Follow these steps to set up and run the game on your local machine.

### 1. Install Python

Ensure that Python 3 is installed on your computer. You can check by running:

```bash
python --version
```

*(On macOS/Linux, you may need to use `python3 --version`.)*  
If Python is not installed, download and install it from the official [python.org](https://www.python.org/) website.

### 2. Clone the Repository

Clone the repository using Git and navigate into the project directory:

```bash
git clone <YOUR-REPOSITORY-URL>
cd The-Club-PyGame
```

### 3. Create a Virtual Environment (Recommended)

Creating a virtual environment helps keep dependencies clean and isolated.

- **Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Dependencies

Install Pygame using `pip`:

```bash
pip install pygame
```

### 5. Launch the Game

Run the primary script to launch the application:

```bash
python Main_code.py
```

---

## 🎮 Gameplay & Controls

- **Starting a Game:** Click **Play** on the main menu to begin a match.
- **Flipping Cards:** Click any card to reveal its image, then click a second card to find a match.
  - If the cards match, they stay face-up and are added to your matched-pairs total.
  - If they do not match, both cards turn face-down again after a brief pause.
- **Move Counter:** Every pair of flips increments the move counter so you can track your efficiency.
- **Winning:** Complete the board by uncovering all 21 pairs to trigger the win condition.
- **Restarting:** Click the **Restart** button at any time to reshuffle the cards and reset the board.
- **Returning to Menu:** Click the **Menu** button to exit the board and return to the title screen.
- **Audio & Settings:** Open **Settings** from the menu to toggle background music on or off and adjust the music volume slider.

---

## 🖼️ Asset Configuration

All game media must be placed inside the `assets/` directory according to the paths defined below. **Filenames, paths, and file extensions (`.png`, `.mp3`) must match exactly**:

| Asset | Path | Description |
| :--- | :--- | :--- |
| **Background Image** | ![alt text](Assets/extra_file/background.png) | Background graphic for menu and gameplay views. |
| **Card Back** | ![alt text](Assets/extra_file/Card_Back.png) | Graphic displayed when cards are face-down. |

> **Note:** Operating systems like Linux and macOS are case-sensitive. Verify that your filenames match the exact capitalization referenced in `Main_code.py`.

---

## 🛠️ Troubleshooting

- **`ModuleNotFoundError: No module named 'pygame'`**
  - Pygame is not installed in your active environment. Run `pip install pygame` (or verify that your virtual environment is activated before running the command).
- **Missing or Misplaced Images:**
  - If card faces or backgrounds fail to display, check that the `assets/images/` and `assets/tiles/` folders exist and that all filenames match the expected patterns. The game includes fallback handling, but correct assets are required for full visual elements.
- **Audio Loading / Playback Errors:**
  - If the game displays an audio warning or music does not play, ensure `background.mp3` is located in `assets/music/` and that an active sound output device is connected to your system. Check the in-game Settings menu to ensure audio is not toggled off.

---

## 🔮 Future Improvements

- [ ] Add selectable difficulty levels (e.g., smaller boards for faster rounds).
- [ ] Implement a timer or speed-run challenge mode.
- [ ] Add sound effects for card flips, successful matches, and victory.
- [ ] Track local high scores and best move records.
- [ ] Add selectable visual themes and alternative card sets.

---

## 👥 Credits & Acknowledgments

- **Game Development:** Amir Ali
- **Programming Language:** Python
- **Game Library:** Pygame
- **Graphics:** Custom assets and external artwork, where applicable.
- **Audio:** Background music, where applicable.

External artwork and audio credits should be added here when the original sources and applicable licenses are confirmed.

---

## 📄 License

> **Note for the repository owner:**  
> Before publishing or claiming an open-source license for this project, choose and add an official license file (such as `LICENSE` using MIT, Apache 2.0, or GPL) to the repository, and update this section accordingly.

---

## 🤝 Explore & Contribute

Thank you for checking out **Tile Club – Match Puzzle Game**! Feel free to clone the repository, test your memory, open issues, or submit pull requests with improvements. Have fun playing!