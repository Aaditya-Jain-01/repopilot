# ⚡ RepoPilot

> Autonomous code security audit, unified self-healing patcher, and synthetic test engineer powered by open-source inference models on **Adaption** and **BharatCode**.

RepoPilot automates multi-stage code reviews. It scans source files for vulnerabilities, anti-patterns, and edge cases, renders unified diff patches ready for review or immediate application, and writes test suites to verify fixes.

---

## 🚀 Key Features

- 🔍 **Static & AST Inference Audit:** Pinpoints SQL injections, resource leaks, unhandled exceptions, and algorithmic bottlenecks with line-level precision.
- 🛠️ **Unified Diff Patch Generation:** Generates valid, `git apply`-compatible unified patches without conversational clutter.
- 🧪 **Autonomous QA Suite:** Synthesizes ready-to-run `pytest` test suites covering edge cases, happy paths, and boundary conditions.
- 🖥️ **Rich Developer CLI:** Built using Rich and Click for terminal tables, syntax highlighting, and progress indicators.
- ⚡ **Open-Source Model Inference:** Integrates with Adaption-hosted inference stacks (`DeepSeek-V4-Flash` / `Qwen-Coder`).

---

## 🛠️ Architecture


```

[Target Source File / Git Diff]
              │
              ▼
   ┌───────────────────────┐
   │    RepoPilot CLI      │
   │    (Click + Rich)     │
   └──────────┬────────────┘
              │ (Prompt Pipeline)
              ▼
   ┌───────────────────────┐
   │ Adaption Inference    │ ◄── (DeepSeek V4 Flash Stack)
   │ Base API / BharatCode │
   └──────────┬────────────┘
              │
      ┌───────┴────────┐
      ▼                ▼
[Unified Diff]    [Pytest Suite]
      │                │
      ▼                ▼
(.patch File)     (test_*.py)

```

---

## 📦 Quick Start

### 1. Clone & Set Up Virtual Environment
```bash
git clone [https://github.com/Aaditya-Jain-01/repopilot.git](https://github.com/Aaditya-Jain-01/repopilot.git)
cd repopilot
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt

```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
ADAPTION_API_KEY=your_adaption_api_key
ADAPTION_ENDPOINT=[https://api.prod.adaptionlabs.ai/api/v1/responses](https://api.prod.adaptionlabs.ai/api/v1/responses)
ADAPTION_MODEL=stack:deepseek-v4-flash-1

```

### 3. Usage Commands

#### Security & Quality Audit

```bash
python cli.py scan demo_target.py

```

#### Autonomous Patch & Self-Healing

```bash
# Preview diff and prompt to apply
python cli.py patch demo_target.py

# Force apply patch directly
python cli.py patch demo_target.py --apply

```

#### Edge-Case Test Suite Synthesis

```bash
python cli.py gentest demo_target.py
pytest test_demo_target.py

```

---

## 🏆 BharatCode Build League

Built for the **BharatCode Build League (Nov 2026)** to showcase developer tooling utilizing open-source inference stacks.


Save (**Ctrl + S**), close Notepad, and push it:

```
git add README.md
git commit -m "docs: add architecture diagram, feature breakdown, and quickstart guide"
git push

```
