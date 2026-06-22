# 🧙 Prompt Wizarding Studio

> *Where prompts are spells, and the best wizard wins.*

Welcome to **Prompt Wizarding Studio** — an interactive playground that puts the three classic prompt engineering techniques head-to-head on any task you throw at them, scores their responses with an LLM-as-judge evaluator, and then dares **you** to write a prompt good enough to beat all three.

This isn't just a demo. It's a hands-on way to *see* prompt engineering work in real time — and to find out if you've actually learned it.

---

### 🔗 [Try it live](https://promptwizardingstudio.streamlit.app)

![Prompt Wizarding Studio screenshot](demo.png)

---

## ✨ What it does

| Step | What happens |
|---|---|
| 1️⃣ You ask anything | From "explain photosynthesis" to "solve this equation" |
| 2️⃣ Task gets classified | Automatically sorted into factual, classification, creative, reasoning, or summarization |
| 3️⃣ Three techniques compete | Zero-shot, Few-shot, and Chain-of-Thought each generate a response |
| 4️⃣ LLM judge scores all three | Out of 100, on relevance, completeness, length, and clarity |
| 5️⃣ You enter the arena | Write your own prompt and try to beat all three techniques |

---

## ⚔️ The Three Techniques

**🎯 Zero-shot** — No help, no examples. Just the raw question and the model's best attempt.

**📚 Few-shot** — Shown relevant example answers first, matched to your task type, so it learns the pattern before answering.

**🧠 Chain-of-Thought** — Explicitly asked to reason step by step before reaching a conclusion. Best for logic, math, and complex problems.

---

## 🏆 Why this is more than a side-by-side comparison

Most prompt comparison tools just show three answers and call it a day. Prompt Wizarding Studio goes further:

**Dynamic few-shot selection**
A classifier detects the task type first — so few-shot always gets genuinely relevant demonstrations, not the same two generic examples every time.

**A judge that actually differentiates**
Built and iterated to avoid score inflation, penalize unnecessary length, and reward concise answers when concise is correct. No more 95/96/97 for everything.

**Structural position-bias mitigation**
The judge evaluates responses across 3 different orderings and averages the scores — structurally eliminating positional bias rather than relying on prompt instructions alone. In testing, positional bias was detected in 26% of evaluations overall (42% on simple tasks, 13% on complex tasks), confirming the correction is meaningful, not cosmetic.

**Weak-model response generation**
Responses are generated on a deliberately lighter model (`gemini-3.1-flash-lite`), so the *techniques themselves* — not raw model power — are what's actually being tested. The judge and classifier run on a stronger model for reliable evaluation.

**Retry logic**
All API calls retry automatically on transient failures, so your run never crashes mid-comparison.

---

## 🧙 The Prompt Wizard Challenge

After seeing all three technique scores, you get a chance to write your own prompt for the same task.

The judge scores your prompt on two dimensions:
- **80 points** — quality of the response your prompt produced
- **20 points** — quality of the prompt itself (clarity, constraints, structure)

Beat all three techniques and earn the title of **Prompt Wizard** 🧙‍♂️

---

## 🛠️ Tech Stack

| Tool | Role |
|---|---|
| Streamlit | Web interface |
| Google Gemini API (`google-genai`) | Response generation, classification, judging |
| Pydantic | Schema-enforced structured JSON outputs |
| python-dotenv | Environment-based API key management |

---

## 📦 Installation

**1. Clone the repo**
```bash
git clone https://github.com/rishidakshbansal2004-create/PromptWizardingStudio.git
cd PromptWizardingStudio
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up API keys**

This project uses the **free tier** of the Gemini API — no billing required.

Get a free key from [Google AI Studio](https://aistudio.google.com) and create a `.env` file:

```env
Res_Gem_Api_Key=your_first_api_key_here
Gem_Api_Key=your_second_api_key_here
```

> 💡 Two keys split API calls across generation and judging stages to stay within free-tier rate limits. You can use the same key twice if you prefer.

**5. Run the app**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 🎮 How to use it

1. Type any question or task → click **Run comparison**
2. Watch three techniques compete and get scored
3. Click **🧙 Are you a Prompt Wizard? Show us!**
4. Write your own prompt → submit → see your rank
5. Click **🔄 New Comparison** to start fresh

---

## 📁 Project Structure
PromptWizardingStudio/
├── app.py          # Streamlit UI, session state, API orchestration
├── prompt.py       # All prompt functions — zero-shot, few-shot, CoT, judge, classifier
├── requirements.txt
├── .env            # API keys (not committed)
└── README.md

---

## 🔮 What I learned building this

**Technique × model strength interaction** — Few-shot and CoT show clearer advantages on weaker models. Strong models often perform well even with zero guidance, which changes which technique "wins."

**LLM judges need deliberate bias engineering** — Score inflation and positional bias are real and documented. Prompt-level instructions help but aren't enough — structural mitigation (response-order randomization) is more robust.

**Few-shot teaches style, not just content** — Generic short examples accidentally make every few-shot response terse, regardless of what the task actually needs. Example design matters more than it seems.

**Structured outputs > asking nicely for JSON** — Schema-enforced Pydantic outputs are far more reliable than "please respond in JSON format" and far easier to build on top of.

---

## 🚧 Future ideas

- User-selectable models per technique — directly compare technique effectiveness across model tiers
- History and leaderboard of past prompt attempts
- Additional techniques — self-consistency, role-prompting, few-shot CoT hybrids

---

Built with curiosity, a lot of debugging, and zero shortcuts — by Rishi.

*May the best prompt win.* 🧙‍♂️✨