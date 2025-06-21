# Contributing to OpenSpeak

🙏 **Thank you for considering a contribution!** This project is powered by an amazing community of users and developers. The guidelines below are here to make the process smooth for everyone.

## Table of Contents
1. Getting Help
2. Reporting Bugs
3. Requesting Features
4. Development Setup
5. Coding Conventions
6. Commit Messages & PRs
7. Code of Conduct

---

## 1. Getting Help
If you have general questions, open a **Discussion** on GitHub. Please avoid filing issues for usage questions.

## 2. Reporting Bugs
Use the **Bug Report** issue template and include:
* Steps to reproduce (with minimal code if possible)
* Expected vs. actual behaviour
* Screenshots or logs
* Your environment (Windows version, Python version, GPU, etc.)

## 3. Requesting Features
Use the **Feature Request** template to describe:
* The problem you are trying to solve
* Why it is valuable to others
* Any ideas for implementation

We love constructive feedback, but we can't promise to implement every idea.

## 4. Development Setup
1. **Fork** this repository and clone your fork:
   ```powershell
   git clone https://github.com/<your-username>/whisper-windows.git
   cd whisper-windows
   ```
2. Create and activate a virtual-env:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate  # (or source venv/bin/activate on WSL/Linux)
   ```
3. Install dependencies for **development**:
   ```powershell
   pip install -r requirements.txt -r requirements-dev.txt
   ```
4. Run the app in editable-install mode to see live changes:
   ```powershell
   python main.py
   ```
5. Run the test & lint suite (if present) before you commit:
   ```powershell
   pytest
   black --check .
   flake8
   ```

> Don't worry if you don't have access to a GPU – CPU mode works fine for development.

## 5. Coding Conventions
* **Python ≥ 3.10**
* PEP-8 compliant, auto-formatted with **Black** (`black .`).
* Keep functions short & focused – prefer composition over large multi-purpose blocks.
* Add (or update) docstrings for public functions/classes.
* UI strings should be stored in `openspeak/assets` where possible for easy localisation.

## 6. Commit Messages & Pull Requests
* Follow the **Conventional Commits** style where practical (`feat:`, `fix:`, `docs:`, etc.).
* Keep commits focused – avoid bundling unrelated changes.
* **Describe _what_ and _why_, not just _how_**.
* Make sure your PR targets the `main` branch and passes CI.
* Add screenshots / GIFs if your change impacts the UI.
* If your PR fixes an Issue, add `Fixes #<number>` to the description.

## 7. Code of Conduct
By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Thank you for helping us keep OpenSpeak welcome & inclusive! ✨ 