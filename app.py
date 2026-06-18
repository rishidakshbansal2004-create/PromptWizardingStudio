import streamlit as st
from google import genai
from prompt import zero_shot_prompt, few_shot_prompt, cot_prompt, judge_prompt,classify_task_prompt
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Literal
import time

load_dotenv()
api_key_resp = os.getenv("Res_Gem_Api_Key")
client1 = genai.Client(api_key=api_key_resp)
api_key_judge = os.getenv("Gem_Api_Key")
client2 = genai.Client(api_key=api_key_judge)

st.title("🚀 Prompt Score Studio")
class TaskType(BaseModel):
    category: Literal["factual", "classification", "creative", "reasoning", "summarization"]
class JudgeResult(BaseModel):
    zero_shot_score: int
    few_shot_score: int
    cot_score: int
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
task = st.text_input("Ask anything...:")
if st.button("Run comparison"):
    with st.spinner("🚀Analysing the Task..."):
        class_response = client2.models.generate_content(
            model="gemini-2.5-flash",
            contents=classify_task_prompt(task),
            config={
                "response_mime_type": "application/json",
                "response_schema": TaskType,
            },
        )
    task_category = class_response.parsed.category
    with st.spinner("🤖 Generating 1st response..."):
        resp1 = call_with_retry(client1, "gemini-2.5-flash-lite", zero_shot_prompt(task))
    with st.spinner("🤖 Generating 2nd response..."):
        resp2 = call_with_retry(client2, "gemini-2.5-flash-lite", few_shot_prompt(task, task_category))
    with st.spinner("🤖 Generating 3rd response..."):
        resp3 = call_with_retry(client1, "gemini-2.5-flash-lite", cot_prompt(task))
    with st.spinner("⚖️ Judging responses..."):
        judge_response = client1.models.generate_content(
        model="gemini-2.5-flash",
        contents=judge_prompt(task, resp1.text, resp2.text, resp3.text),
        config={
            "response_mime_type": "application/json",
            "response_schema": JudgeResult,
        },
        )
    if judge_response.parsed is None:
       st.error("UNEXPECTED ERROR OCCURED JUDGMENT COUDN'T BE PASSED")
       st.write(judge_response.text)
       st.stop()

    result = judge_response.parsed
 
    col1, col2, col3 = st.columns([1,1,1.1])
    
    with col1:
        st.subheader("Zero-shot")
        with st.container(height=300):
            st.write(resp1.text)
        st.metric("Score", f"{result.zero_shot_score}/100")
        st.progress(result.zero_shot_score / 100)
    
    with col2:
        st.subheader("Few-shot")
        with st.container(height=300):
            st.write(resp2.text)
        st.metric("Score", f"{result.few_shot_score}/100")
        st.progress(result.few_shot_score / 100)

    with col3:
        st.subheader("Chain-of-Thought")
        with st.container(height=300):
            st.write(resp3.text)
        st.metric("Score", f"{result.cot_score}/100")
        st.progress(result.cot_score / 100)
    

    st.divider()
    st.success(f"🏆 Best technique: {result.best_technique} — REASON BEHIND THE CHOICE: {result.reasoning}")
