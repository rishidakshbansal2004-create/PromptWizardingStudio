# 🧙 Building Prompt Wizarding World — A Build Journal

This is the story of how I built **Prompt Wizarding World**, from "what even is prompt engineering" to a working app that judges three classic prompting techniques head-to-head — and then challenges you to beat them with your own prompt.

I wanted to write this down because the finished repo doesn't show the actual process: the wrong turns, the debugging, the moments where a "simple" feature turned out to need a real design decision. If you're learning this stuff too, I hope this is useful. If you're reviewing this as a portfolio piece, this is the part that doesn't fit in commit messages.

---

## The idea

It started from a suggestion: build a "Prompt Engineering Playground" — something that tests different prompting techniques side by side, so you can actually *see* how zero-shot, few-shot, and chain-of-thought differ, instead of just reading about them.

I liked it immediately, but I had a real concern early on: wasn't this too basic? Three boxes showing three outputs felt like something a tutorial would have you build in an afternoon. I didn't want a project that looked like I'd followed a recipe.

The answer turned out to be: the *techniques* are simple by design — that's not a flaw, that's literally what defines zero-shot/few-shot/CoT in the research. The depth had to come from somewhere else — from building a way to actually *measure* which technique wins, and why. That one decision — adding an LLM judge that scores each response — is what turned this from "look, three outputs" into a real, opinionated tool with something to say.

---

## Picking the stack

Before writing any code, I had to decide which LLM API to use. I looked at Claude, OpenAI, and Gemini. The deciding factor wasn't capability — it was Gemini's free tier. No credit card, real headroom (roughly 15 requests/minute, ~1,500/day on the free Flash models), and no real cost risk while I was still learning and likely to make mistakes. That last point mattered more than I expected — knowing I couldn't accidentally rack up a bill made me much more willing to experiment and break things.

For the interface, I already knew Streamlit from an earlier housing-price-prediction project, so I didn't have to learn a new UI framework on top of everything else. In hindsight, this was the right call — Streamlit caused me *plenty* of trouble on its own (more on that later), and trying to learn a second framework at the same time would have been a lot.

---

## First real stumble: the API key didn't work

My very first script — three lines, just trying to get a single response back from Gemini — failed with a `PERMISSION_DENIED` / 403 error. I went through the usual suspects: typo in the key, missing characters, region restrictions. None of it.

The actual cause: I'd generated the API key under one Google account, then switched to a different Google account in my browser session without realizing the key was tied to the original one. Once I switched back, it worked instantly. Not a code problem at all — a reminder that "it's broken" doesn't always mean the code is wrong.

---

## Learning the actual techniques by writing them, not reading about them

Before touching the API in a loop, I wrote three functions — `zero_shot_prompt`, `few_shot_prompt`, `cot_prompt` — each one just building a different string from the same input task. No API calls yet, just string construction.

Zero-shot was trivial: just return the task as-is, no wrapping.

Few-shot needed two generic example Q&A pairs before the real task, so the model would pick up the *pattern* before answering. I picked unrelated trivia examples at first (capital of Japan, boiling point of water) — this turned out to be a mistake I wouldn't discover until much later.

Chain-of-Thought was where I learned something real about technique boundaries. My first attempt at a CoT prompt actually included a full worked example showing step-by-step reasoning about how to make tea — which I was proud of, until I realized I'd accidentally invented a "few-shot + CoT hybrid," not pure CoT. Pure CoT doesn't need an example at all — it's just the task plus an instruction like "let's think step by step." If I'd kept my version, I would have been comparing "examples alone" against "examples + reasoning trigger," not "examples" against "reasoning trigger alone" — which would have made the whole comparison meaningless. Small mistake, but it taught me to actually respect what each technique is testing, not just bolt things together because they seemed like they'd work better.

---

## Connecting it all and seeing the difference for the first time

Once all three prompt functions existed, I wrote a test script that called Gemini three times — once per technique — on the same task ("explain how a refrigerator keeps food cold") and printed all three responses.

This was the first genuinely exciting moment in the project. Zero-shot gave a long, complete, well-structured answer on its own — no help needed. Few-shot gave a noticeably shorter, more condensed version of the same content. Chain-of-Thought gave the longest, most deliberate-feeling answer, with extra framing sections before even reaching the actual steps.

Seeing those three genuinely different outputs side by side — not just reworded versions of each other — was the moment the project stopped feeling like "I'm following instructions" and started feeling like "I'm actually seeing something real about how these techniques behave."

---

## Streamlit: my first real wall

Getting the three-call script working in the terminal was one thing. Getting it into an actual web UI was where I hit my first proper wall.

I wrote the Streamlit version, ran `streamlit run app.py`, and got a **completely blank white screen**. No error in the terminal. No error in the browser. Just nothing.

I went through this methodically:
- Checked if `streamlit` was actually imported (it was)
- Manually copy-pasted the local URL instead of relying on the auto-opened tab
- Hard-refreshed, tried a different browser
- Eventually isolated it: I was running this inside VS Code's integrated terminal on a Mac, and the link-click behavior from there can open VS Code's own internal preview pane instead of a real browser — which silently failed to render Streamlit properly.

The fix was almost embarrassingly simple once found: close that internal preview, manually open an actual standalone browser app, and paste the URL there directly. Nothing was wrong with my code at all — it was an environment quirk specific to that exact combination of tools (VS Code terminal + Mac + Streamlit's auto-launch behavior).

This was a good early lesson: not every bug is a code bug. Sometimes it's the five layers of tooling underneath your code.
## Building the judge — and immediately hitting its limits

Once the three-way comparison worked, I wanted more than "look at three boxes" — I wanted the app to actually *score* each response, so there was a real verdict, not just raw output. This became the LLM-as-judge feature: a fourth API call that takes the task and all three responses, and scores them.

My first version asked the model to respond strictly in JSON so I could parse the scores programmatically. That worked, technically — but it was fragile. The model would occasionally wrap the JSON in extra text ("Sure, here are the scores:") which broke a plain `json.loads()` call. I switched to Gemini's structured output feature instead — defining a Pydantic schema (`zero_shot_score`, `few_shot_score`, `cot_score`, `best_technique`, `reasoning`) and passing it as `response_schema`, which guarantees valid, parseable JSON at the API level instead of hoping the model behaves. This was a much cleaner fix than trying to out-prompt the formatting problem.

### Problem 1: every score came back 100/100/100

The first time I got real scores flowing into the UI, all three techniques scored a perfect 100 on a simple math question. Three identical perfect scores told me nothing — a judge that always says "everyone's perfect" provides zero actual signal, which defeats the entire purpose of having one.

The real cause was score inflation — a known, documented issue with LLM-as-judge setups in general. Without explicit pressure to differentiate, models default to generous, non-committal scoring. I fixed this by rewriting the judge prompt to: explicitly frame the task as relative ranking (rank the three responses first, *then* assign scores reflecting that ranking), set a numeric expectation (most good responses should land 60–92, with 100 reserved for genuinely flawless answers), and instruct the model not to default to identical or near-identical scores unless responses were truly indistinguishable.

### Problem 2: the judge was secretly rewarding length

Once scores started differentiating, I noticed something else — longer answers tended to win, even when a shorter, more direct answer would have been objectively correct (the classic "what's the capital of France" case, where "Paris" is the *right* answer, not an incomplete one). I added an explicit criterion telling the judge that conciseness is a virtue when the task doesn't need depth, and that padding without added value should be penalized — not just tolerated.

### Problem 3: I'd accidentally built an unfair judge myself

This one stung a little, because I'd written it myself without noticing. My judging criteria included a line that specifically scrutinized few-shot for "did it follow the example pattern" and CoT for "did it show genuine reasoning, or just write more text" — but said nothing equivalent about zero-shot. I'd given two of the three techniques an extra way to lose points, and given the third a free pass. It wasn't malicious, it was just an oversight from writing technique-specific checks for the techniques that have an obvious definition (few-shot = followed the pattern?, CoT = genuine reasoning?) while zero-shot's "definition" is just "no help given" — so I never wrote an equivalent trap for it.

The fix was to drop technique-specific scrutiny from being a separate criterion entirely, and fold "did it use its context well" evenly into the general evaluation — so all three responses are held to the exact same bar, with no technique getting special skepticism.

### Problem 4: position bias

I'd read that LLM judges can favor whichever response appears first in a prompt, regardless of actual content. I tested this directly — reordered the three responses in the judge prompt without changing their content, and watched whether scores shifted. They did, somewhat. I added an explicit instruction telling the judge to evaluate all three simultaneously before scoring any of them, to treat this as a comparative (not absolute) evaluation, and to be aware of and actively counteract any tendency to favor responses based on their position in the sequence.

---

## Few-shot's hidden flaw: my examples were teaching the wrong lesson

After fixing the judge, I noticed few-shot kept scoring lower — and dug into why. My original few-shot examples were short, one-line trivia answers ("Q: capital of Japan? A: Tokyo"). The model was faithfully copying that *style* — short, direct answers — regardless of whether the actual task needed depth. So when someone asked "explain how a refrigerator works," few-shot gave a noticeably terser answer than zero-shot or CoT, not because few-shot is a worse technique, but because my examples had trained it to be artificially brief.

This was a genuinely useful realization: few-shot examples don't just teach *content patterns*, they teach *length and depth* too. I rewrote every category's examples (factual, classification, creative, reasoning, summarization) to model *appropriate* depth for that category — full, well-reasoned explanations for factual and reasoning examples, genuinely short answers for classification (where brevity is actually correct), real creative writing for the creative category.

While rewriting the reasoning examples specifically, I also caught myself making a second version of the same mistake in a different dimension: my first two reasoning examples were both math (an algebra equation, a train speed problem). If I'd left it there, the model might have learned "reasoning = numbers," and underperformed on a reasoning task with no math involved at all. I added a third example — a qualitative deduction problem (why a plant in a dark closet has wilted, yellow leaves) — specifically to cover non-quantitative reasoning too.

---

## Adding task classification — and a 5th category I almost missed

To make few-shot's examples actually relevant to whatever the user asks, I added a classification step: a separate API call that sorts the user's task into one of several fixed categories before picking which example set to show. I started with four categories (factual, classification, creative, reasoning), but realized a real gap — summarization/extraction tasks ("summarize this paragraph," "pull out the key dates") didn't cleanly fit any of the four. I added a fifth category specifically for this.

This is also where I learned about Pydantic's `Literal` type — constraining a field to one of a fixed set of exact string values, so the classifier's output can't drift into some category my code doesn't know how to handle.

---

## Chain-of-Thought's overhead problem

Once I started testing with a deliberately weaker model (`gemini-2.5-flash-lite`, swapped in specifically so the techniques themselves — not raw model power — would be what's being tested), I noticed something odd: CoT kept *losing* to zero-shot on simple, unambiguous math problems, even though CoT is supposed to help reasoning.

Looking closely, the cause was visible right in the output: my CoT prompt forced four mandatory steps, starting with "identify exactly what is being asked" — which is genuinely useful for ambiguous questions, but pure overhead on a question that's already crystal clear. That extra restating-the-obvious text was triggering my own judge's "penalize length that doesn't add value" criterion.

I rewrote the CoT prompt to make the four steps flexible guidance rather than a rigid checklist — explicitly telling the model to skip any step that doesn't add value for that specific task, and not to pad reasoning with unnecessary restatement.

I had a hypothesis here worth mentioning: I suspected a *weaker* model might actually do better with the original rigid, mandatory version, since deciding what to skip requires its own judgment call, which a lighter model might handle less reliably than a stronger one. I tested both versions directly on the weak model. The flexible version still won. The hypothesis was reasonable, but the data didn't support it — so I went with what the test actually showed, not what the theory predicted.
## What the weak-model experiment actually revealed

Switching response generation to `gemini-2.5-flash-lite` while keeping classification and judging on the stronger `gemini-2.5-flash` wasn't just a cost-saving move — it was meant to directly test the project's core premise: does prompting technique actually matter, or does a strong model just make all three techniques look equally fine?

The results were genuinely more interesting than a clean "technique X always wins" story. On a combined-rates math problem (two pipes filling a tank), few-shot won clearly — its worked examples gave a weaker model real structural help that zero-shot didn't have. On an open-ended business diagnosis question ("why did sales drop after a redesign"), zero-shot won instead — likely because that task didn't cleanly match any of my five categories, so few-shot's pattern-matching from a slightly mismatched example set hurt more than it helped.

That's not a flaw in the project — it's the actual finding. Prompting technique effectiveness depends on how well the technique's setup (especially few-shot's examples) matches what the task actually needs. A simple "this technique is always best" conclusion would have been less true, and honestly, less interesting.

I also hit real infrastructure issues running on the weaker, free, heavily-used Flash-Lite model — calls would occasionally stall, seemingly due to demand spikes on Google's end, not anything in my code. I added a retry helper (`call_with_retry`) that wraps every API call in a small loop: try, and if it fails, wait a couple seconds and try again, up to three attempts, before finally surfacing a real error. Small addition, but a genuinely useful, realistic piece of engineering — every robust API integration needs some version of this.

I also split API calls across two separate Gemini API keys (and two client objects) specifically to spread load and stay further under the free tier's per-minute rate limit, since five calls per "Run comparison" click adds up faster than it sounds.

---

## The Prompt Wizard Challenge

The feature I was most excited to build: letting the user write their own full prompt for the same task, and having the judge score it against all three baseline techniques. This needed a clear design decision before any code: should a user's custom prompt be judged in total isolation, or directly against the three techniques that already ran?

I went with direct comparison, anchored to the original three scores — meaning the new judge call doesn't re-evaluate the original three from scratch (which would waste tokens and risk slightly different scores on a second pass), it receives the original three responses *and their already-decided scores* as fixed reference points, and only outputs one new score for the custom prompt. This kept the feature both cheaper (two extra API calls instead of re-running everything) and more consistent (no risk of the judge disagreeing with itself between two separate passes).

One thing I deliberately got right early: I made sure NOT to ask the judge to compare "whose prompt was better" among the original three baseline techniques, since the user didn't write any of those — only their own custom prompt should ever be evaluated as a piece of authored prompt engineering. The three baselines are demonstrations, not entries in the competition.

### Streamlit's rerun model fought me here, hard

This was the single hardest technical stretch of the whole project. Streamlit reruns your *entire script* top to bottom on every single interaction — click a button, type in a box, anything. That means any variable you set normally just vanishes on the next interaction unless you deliberately preserve it.

Getting the four-phase flow working — run comparison, reveal a text box, submit a custom prompt, show four columns, show a ranked popup, reset — meant learning `st.session_state` properly: a dictionary-like object that survives reruns, where I had to explicitly save every piece of state I needed later (the three original responses, their scores, the task itself) right after they were computed, then rewrite my display logic to read *from* session state instead of from the original local variables, since those variables would be gone by the time the next rerun happened.

I hit a genuine wall here more than once — buttons that needed two clicks to register, sections that disappeared when they shouldn't, state that reset when I didn't want it to. I won't pretend I diagnosed every one of these elegantly; some of it was real trial and error, deliberately toggling different session state flags and rerunning until the flow behaved the way I wanted. But I got through it, and understanding *why* it kept breaking (the rerun model, not random bad luck) made the eventual fixes make sense instead of feeling like guesswork.

### Designing the judge's verdict and the popup

For the final ranking popup, I wanted four distinct outcomes depending on where the user's custom prompt landed relative to the three baselines — beating all three earns "Prompt Wizard," beating two is solid, beating one is encouraging but pushes for more practice, and beating none is framed as a learning moment rather than a failure. Small thing, but getting the tone right mattered to me — I wanted losing to feel like useful information, not a dead end.

---

## Smaller decisions worth recording

A few smaller things I made deliberate calls on, that don't deserve their own section but mattered at the time:

**Two API keys, deliberately split** — once I realized five API calls per click could hit the free tier's per-minute limit after just a few rapid test runs, I split calls across two separate Gemini API keys, roughly 3-2, specifically to spread load rather than bottleneck on one key.

**Never hardcoding API keys** — every key lives in a `.env` file, loaded via `python-dotenv`, and the `.env` file itself is excluded from version control. This matters more than it sounds like it should; an exposed key in a public repo is a real, avoidable risk, and building the habit early was worth the extra five minutes of setup.

**A sidebar walkthrough I added on my own** — once the core app worked, I added a short guided sidebar explaining each technique in plain language, with next/previous navigation, so the app teaches the concepts it's demonstrating, rather than assuming the visitor already knows what zero-shot or chain-of-thought means.

---

## What I'd genuinely tell someone starting this project

Don't skip writing the prompt functions yourself, even when it's tempting to just take a working version and move on. The few-shot length bug, the CoT overhead problem, the asymmetric judge criteria — I only caught all three because I'd actually written and understood every line well enough to notice when behavior didn't match intent. If I'd just copied a working version blindly, I might have shipped a judge that was secretly unfair, and never known why scores looked the way they did.

Test your assumptions instead of trusting them. The "stronger model = always better, technique doesn't matter as much" worry, the "rigid CoT will help a weak model more" hypothesis, the "judge favors response position" suspicion — I could have just guessed at all three. Testing them directly, even with a handful of manual trials, turned vague guesses into actual findings I can stand behind.

And accept that some bugs aren't your code's fault. The blank Streamlit screen from a VS Code-specific browser quirk, the 403 error from a Google account mismatch — neither of those came from a mistake in my logic, and I'd have wasted a lot more time if I'd kept assuming the bug had to be in my Python.

---

*Built by Rishi. Still learning. Still debugging.* 🧙‍♂️
