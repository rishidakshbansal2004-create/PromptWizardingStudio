import streamlit as st
from google import genai
from prompt import zero_shot_prompt, few_shot_prompt, cot_prompt, judge_prompt,classify_task_prompt,judge_custom_prompt
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Literal
import time

load_dotenv()
api_key_resp = os.getenv("Res_Gem_Api_Key")

if not api_key_resp:
    try:
        api_key_resp = st.secrets["Res_Gem_Api_Key"]
    except:
        pass
client1 = genai.Client(api_key=api_key_resp)

api_key_judge = os.getenv("Gem_Api_Key")
if not api_key_judge:
    try:
        api_key_resp = st.secrets["Gem_Api_Key"]
    except:
        pass
client2 = genai.Client(api_key=api_key_judge)

import streamlit as st

st.set_page_config(
    page_title="Prompt Wizarding Studio",
    page_icon="🚀",
    layout="wide"
)
st.title("🚀 Prompt Wizarding Studio")
class TaskType(BaseModel):
    category: Literal["factual", "classification", "creative", "reasoning", "summarization"]
class JudgeResult(BaseModel):
    zero_shot_score: int
    few_shot_score: int
    cot_score: int
    best_technique: str
    reasoning: str

class CustomJudgeResult(BaseModel):
    custom_score: int
    best_technique: str
    reasoning: str

def call_with_retry(client, model, contents, config=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            if config:
                return client.models.generate_content(model=model, contents=contents, config=config)
            else:
                return client.models.generate_content(model=model, contents=contents)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise e
if "guide_step" not in st.session_state:
    st.session_state.guide_step = 0

slides = [
    {
        "title": "🧙 Welcome to the Prompt Wizarding World",
        "text": "Here you'll discover how different prompting techniques change AI responses."
    },
    {
        "title": "🎯 Zero-shot Prompting",
        "text": "Ask the AI directly without examples. Fast and simple, but not always the most accurate."
    },
   {
    "title": "📚 Few-Shot Prompting",
    "text": """
Few-shot prompting means giving examples before asking the real task.

Example:

Input: I love this movie

Output: Positive

Input: This is terrible

Output: Negative

Now the model learns the pattern and can classify new examples more accurately.
"""
},
    {
        "title": "🧠 Chain-of-Thought",

        "text": """Encourage step-by-step reasoning. 

        Great for logic, math, and complex tasks.

        Example: 'Let's think step by step' or 'First, we do this...

        This often leads to more accurate and detailed responses."""
    },
    {
        "title": "🏆 Prompt Wizard Challenge",
        "text": "After comparing all techniques, create your own prompt and try to beat them!"
    }
]

current = slides[st.session_state.guide_step]

st.sidebar.markdown(f"## {current['title']}")
st.sidebar.write(current["text"])

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("⬅ Previous", disabled=st.session_state.guide_step == 0):
        st.session_state.guide_step -= 1
        st.rerun()

with col2:
    if st.button("Next ➡", disabled=st.session_state.guide_step == len(slides)-1):
        st.session_state.guide_step += 1
        st.rerun()
st.sidebar.divider()
st.sidebar.markdown("Welcome young wizard! This wizarding school is made by Rishi to test your prompt engineering skills. Use the navigation above to explore the techniques, then head back here to try your own custom prompt and see if you can outperform the classics! May the best prompt win! 🧙‍♂️✨")
st.sidebar.divider()
if st.sidebar.button(
    "🔄 New Comparison",
    use_container_width=True
):
    st.session_state.clear()
    st.rerun()

if not st.session_state.get("comparison_done", False):
    
    task = st.text_input("Ask anything...:")

    if st.button("Run comparison") and task.strip():
        with st.spinner("🚀Analysing the Task..."):
            class_response = call_with_retry(
                client1,
                "gemini-3.1-flash-lite",
                classify_task_prompt(task),
                config={
                    "response_mime_type": "application/json",
                    "response_schema": TaskType,
                },
            )

        task_category = class_response.parsed.category

        with st.spinner("🤖 Generating 1st response..."):
            resp1 = call_with_retry(client1, "gemini-3.1-flash-lite", zero_shot_prompt(task))

        with st.spinner("🤖 Generating 2nd response..."):
            resp2 = call_with_retry(client2, "gemini-3.1-flash-lite", few_shot_prompt(task, task_category))

        with st.spinner("🤖 Generating 3rd response..."):
            resp3 = call_with_retry(client1, "gemini-3.1-flash-lite", cot_prompt(task))

        with st.spinner("⚖️ Judging responses (bias-corrected)..."):
            orderings = [
            (resp1.text, resp2.text, resp3.text, "Zero-shot", "Few-shot", "CoT"),
            (resp2.text, resp3.text, resp1.text, "Few-shot", "CoT", "Zero-shot"),
            (resp3.text, resp1.text, resp2.text, "CoT", "Zero-shot", "Few-shot"),
            ]

            all_zero_scores = []
            all_few_scores = []
            all_cot_scores = []
            all_winners = []

            for r1, r2, r3, l1, l2, l3 in orderings:
                result = call_with_retry(
                client1,
                "gemini-2.5-flash",
                judge_prompt(task, r1, r2, r3, l1, l2, l3),
                config={
                "response_mime_type": "application/json",
                "response_schema": JudgeResult,
                },
                )
                if result.parsed is None:
                    st.error("UNEXPECTED ERROR OCCURED JUDGMENT COULDN'T BE PASSED")
                    st.write(result.text)
                    st.stop()

                all_zero_scores.append(result.parsed.zero_shot_score)
                all_few_scores.append(result.parsed.few_shot_score)
                all_cot_scores.append(result.parsed.cot_score)
                all_winners.append(result.parsed.best_technique)

            final_zero = round(sum(all_zero_scores) / 3)
            final_few = round(sum(all_few_scores) / 3)
            final_cot = round(sum(all_cot_scores) / 3)

            best = max(
            [("Zero-shot", final_zero), ("Few-shot", final_few), ("CoT", final_cot)],
            key=lambda x: x[1]
            )[0]

        st.session_state["resp1"] = resp1.text
        st.session_state["resp2"] = resp2.text
        st.session_state["resp3"] = resp3.text
        st.session_state["all_zero_scores"] = all_zero_scores
        st.session_state["all_few_scores"] = all_few_scores
        st.session_state["all_cot_scores"] = all_cot_scores
        st.session_state["zero_score"] = final_zero
        st.session_state["few_score"] = final_few
        st.session_state["cot_score"] = final_cot
        st.session_state["task"] = task
        st.session_state["comparison_done"] = True
        st.session_state["response_done"] = True
        st.session_state["best_technique"] = best
        st.session_state["reasoning"] = f"Consistent winner across 3 evaluation orderings: {all_winners}"

if st.session_state.get("response_done", False):
        st.caption(f"Responses and scores for Task: {st.session_state['task']}")
        col1, col2, col3 = st.columns([1,1,1.1])

        with col1:
            st.subheader("Zero-shot")
            with st.container(height=300):
                st.write(st.session_state["resp1"])
            st.metric("Score", f"{st.session_state['zero_score']}/100")
            st.progress(st.session_state['zero_score'] / 100)

        with col2:
            st.subheader("Few-shot")
            with st.container(height=300):
                st.write(st.session_state["resp2"])
            st.metric("Score", f"{st.session_state['few_score']}/100")
            st.progress(st.session_state['few_score'] / 100)

        with col3:
            st.subheader("Chain-of-Thought")
            with st.container(height=300):
                st.write(st.session_state["resp3"])
            st.metric("Score", f"{st.session_state['cot_score']}/100")
            st.progress(st.session_state['cot_score'] / 100)

        col_left, col_center, col_right = st.columns([1,2,1])
        with col_center:
            if st.button("🧙 Are you a Prompt Wizard? Show us!"):
                st.session_state["show_custom"] = True
                st.session_state["response_done"] = False
                st.rerun()

        st.divider()
        best = st.session_state['best_technique']

        if best == "Zero-shot":
            scores = st.session_state["all_zero_scores"]
            avg = st.session_state["zero_score"]
        elif best == "Few-shot":
            scores = st.session_state["all_few_scores"]
            avg = st.session_state["few_score"]
        else:
            scores = st.session_state["all_cot_scores"]
            avg = st.session_state["cot_score"]
        
        winners = st.session_state["reasoning"]
        flip_detected = len(set(w.lower() for w in winners)) > 1

        st.success(f"🏆 Best technique: {best} — scores across 3 evaluation rounds: {scores[0]}, {scores[1]}, {scores[2]} → avg: {avg}/100")
        if flip_detected:
            st.warning("⚠️ Position bias detected and is mitigated — winner changed across evaluation orderings. Final scores are bias-corrected averages.")

if st.session_state.get("comparison_done", False):

    if st.session_state.get("show_custom", False):

        st.info("💡 Now it's your turn! Write a prompt that you think will outperform")

        custom_prompt = st.text_area(
            "Write your full prompt here:",
            placeholder="Include any instructions, examples, or framing you want the model to use. The task will be appended automatically — just write your prompt strategy...",
            height=150
        )

        col_left2, col_center2, col_right2 = st.columns([1, 2, 1])

        with col_center2:
            submit_clicked = st.button("🚀 Ready to test your skill? Submit your prompt")

        if submit_clicked and custom_prompt.strip():

            st.session_state["show_custom"] = False

            with st.spinner("🤖 Generating response for your prompt..."):
                custom_response = call_with_retry(
                    client2,
                    "gemini-3.1-flash-lite",
                    f"{custom_prompt}\n\n{st.session_state['task']}"
                )

            with st.spinner("⚖️ Judging your prompt..."):
                custom_judge_config = {
                    "response_mime_type": "application/json",
                    "response_schema": CustomJudgeResult,
                }

                custom_judge_resp = call_with_retry(
                    client1,
                    "gemini-3.5-flash",
                    judge_custom_prompt(
                        st.session_state["task"],
                        st.session_state["resp1"],
                        st.session_state["resp2"],
                        st.session_state["resp3"],
                        st.session_state["zero_score"],
                        st.session_state["few_score"],
                        st.session_state["cot_score"],
                        custom_prompt,
                        custom_response.text
                    ),
                    config=custom_judge_config
                )

            custom_result = custom_judge_resp.parsed

            st.session_state["custom_resp"] = custom_response.text
            st.session_state["custom_score"] = custom_result.custom_score
            st.session_state["custom_reasoning"] = custom_result.reasoning
            st.session_state["custom_best"] = custom_result.best_technique
            st.session_state["show_results"] = True
            st.session_state["custom_prompt"] = custom_prompt

            st.rerun()

    if st.session_state.get("show_results", False):
        st.caption(f"responses and scores for Task: {st.session_state['task']}")
        st.divider()

        col1, col2, col3, col4 = st.columns([1,1,1,1.1])

        with col1:
            st.subheader("Zero-shot")
            with st.container(height=300):
                st.write(st.session_state["resp1"])
            st.metric("Score", f"{st.session_state['zero_score']}/100")
            st.progress(st.session_state["zero_score"] / 100)

        with col2:
            st.subheader("Few-shot")
            with st.container(height=300):
                st.write(st.session_state["resp2"])
            st.metric("Score", f"{st.session_state['few_score']}/100")
            st.progress(st.session_state["few_score"] / 100)

        with col3:
            st.subheader("COT")
            with st.container(height=300):
                st.write(st.session_state["resp3"])
            st.metric("Score", f"{st.session_state['cot_score']}/100")
            st.progress(st.session_state["cot_score"] / 100)

        with col4:
            st.subheader("Your Prompt")
            with st.container(height=300):
                st.write(st.session_state["custom_resp"])
            st.metric("Score", f"{st.session_state['custom_score']}/100")
            st.progress(st.session_state["custom_score"] / 100)

        scores = {
            "Zero-shot": st.session_state["zero_score"],
            "Few-shot": st.session_state["few_score"],
            "COT": st.session_state["cot_score"],
            "user Prompt": st.session_state["custom_score"]
        }

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        user_rank = [i for i, (technique, score) in enumerate(sorted_scores) if technique == "user Prompt"][0] + 1

        if user_rank == 1:
            st.balloons()
            st.snow()
            st.success("You are 🧙 Prompt Wizard! Your prompt outperformed all three techniques. You clearly know how to talk to AI.")
        elif user_rank == 2:
            st.snow()
            st.success("⚡ Strong work! Your prompt beat two out of three techniques. One more refinement and you're unstoppable.")
        elif user_rank == 3:
            st.warning("🎯 Not bad! Your prompt edged out one technique. Keep experimenting — prompt engineering takes practice.")
        else:
            st.error("🤖 The machine wins this round! Study the top-scoring responses and try again — every attempt teaches you something.")

        st.divider()
        st.info(f"⚖️ Judge's verdict: {st.session_state['custom_reasoning']}")

