# 🚀 Quick Start Guide - Level 3

Get the Claude SDK agent running in under 5 minutes!

## Step 1: Navigate to Level-3

```powershell
cd c:\Users\SaiyadUveshali\Desktop\l2-wizard\Level-3
```

## Step 2: Activate Virtual Environment

The virtual environment already exists. Activate it:

```powershell
.venv\Scripts\activate
```

You should see `(.venv)` in your prompt.

## Step 3: Install Dependencies

If you haven't already:

```powershell
pip install -r requirements.txt
```

Or use the automated setup:

```powershell
python setup.py
```

## Step 4: Set Your API Key

You need an Anthropic API key. Get one at: https://console.anthropic.com/

```powershell
# Windows PowerShell
$env:ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

**Important**: Replace `'sk-ant-your-key-here'` with your actual API key!

## Step 5: Run the Agent

### Option A: Interactive Mode

```powershell
python agent.py
```

Then try queries like:
- `"What's the weather in New York at 40.7128, -74.0060?"`
- `"Recommend 3 mystery books"`
- `"Tell me a joke and show a dog pic"`

### Option B: Run Tests

```powershell
python test_agent.py
```

This runs 5 automated test scenarios to verify everything works.

## Troubleshooting

### "ANTHROPIC_API_KEY is required"

Make sure you set the environment variable:

```powershell
$env:ANTHROPIC_API_KEY='your-key-here'
```

### "Module not found"

Activate the virtual environment:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

### Still having issues?

See the full documentation:
- `Level-3/README.md` - Complete Level 3 docs
- `MIGRATION.md` - Migration guide
- Main `README.md` - Overview

---

## What's Next?

- **Explore the code**: Start with `agent.py` to see the agent loop
- **Add your own tools**: Modify `tools.py` to add new capabilities
- **Compare with Level 2**: Run `python ../agent_simple.py` to see the difference
- **Read the docs**: Lots of detail in README files

---

**That's it!** You now have a production-ready Claude SDK agent running. 🎉
