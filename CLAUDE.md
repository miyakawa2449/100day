# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a 100-day coding challenge repository containing various Python projects, each in its own directory with the format `XXX_ProjectName/` where XXX is the day number (001-015).

## Project Types and Common Commands

### 1. Game Projects (Pygame)
**Projects**: 001Day_Othello, 002DayNumberGues, 005Day_Breakout, 006_Tic-Tac-Toe

**Run Command**:
```bash
cd [project_directory]/src  # if src/ exists
python main.py  # or python [game_name].py
```

### 2. Face Recognition Projects (OpenCV/dlib)
**Projects**: 007_Face_Recognition, 008_face_landmark_analyzer, 009_face_memory, 010_face_Recognition, 011_face_Recognition

**Common Dependencies**:
```bash
pip install opencv-python numpy dlib matplotlib
```

**Run Command**:
```bash
python face_recognition.py  # or python main.py
```

### 3. Flask Web Applications
**Projects**: 003Llama3-8B-Youko, 012_AI_Illustrator

**Run Command**:
```bash
python app.py  # or python flask_chatbot.py
```

### 4. Streamlit Applications
**Projects**: 015_stable_diffusion

**Dependencies**:
```bash
pip install -r requirements.txt  # if exists, or:
pip install streamlit requests Pillow
```

**Run Command**:
```bash
streamlit run streamlit_ai.py
```

### 5. Stability AI / Image Generation Projects
**Projects**: 012_AI_Illustrator, 013_Stability_AI, 014_Staibility_AI_Local, 015_stable_diffusion

**Common Dependencies**:
```bash
pip install requests Pillow python-dotenv openai
```

**Environment Setup**: These projects require `.env` file with API keys:
```env
STABILITY_API_KEY=sk-your_stability_ai_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here  # for Japanese translation
```

## Architecture Patterns

### Virtual Environments
Some projects (e.g., 001Day_Othello) use Python virtual environments. Check for `venv/` or similar directories.

### Database Usage
Face recognition projects (009, 010, 011) use SQLite databases (`face_database.db`) for storing face embeddings and person information.

### Asset Organization
- Games store assets in `assets/` or `src/assets/` with subdirectories for `sounds/` and `fonts/`
- Web applications use `templates/` for HTML files
- Generated images are typically saved in project root or `converted_images/`

### API Integration
- Projects 012-015 integrate with external APIs (Stability AI, OpenAI)
- 015_stable_diffusion requires local Stable Diffusion Web UI running with `--api` flag at `http://127.0.0.1:7860`

## Development Guidelines

### Japanese Documentation
Most projects have Japanese README files. Key terms:
- 実行方法 = How to run
- 必要な環境 = Requirements
- 使い方 = Usage
- 注意事項 = Important notes

### Common Patterns
- Entry points are typically `main.py`, `app.py`, or `[project_name].py`
- GUI applications often use Tkinter (number guess) or Pygame (games)
- Web apps use either Flask (simple) or Streamlit (data/AI apps)
- Face recognition projects follow similar patterns using OpenCV for camera access and dlib for face detection

### Testing
No standardized testing framework across projects. Manual testing is typical approach.

### Build/Lint Commands
No project-wide lint or build commands established. Projects are standalone Python applications.