def zero_shot_prompt(task):
    return task

def few_shot_prompt(task, category):
    examples = {
        "factual": """Q: How does a rainbow form?
A: A rainbow forms when sunlight passes through water droplets in the air. As light enters a droplet, it bends (refracts), separating into its different wavelengths, which we see as different colors. The light then reflects off the back of the droplet and bends again as it exits, spreading the colors further into the familiar arc shape we see in the sky.

Q: Why do leaves change color in autumn?
A: Leaves change color in autumn because shorter days and cooler temperatures cause trees to stop producing chlorophyll, the green pigment that absorbs sunlight for photosynthesis. As chlorophyll breaks down, other pigments that were always present in the leaf — like yellow and orange carotenoids — become visible. In some trees, new red and purple pigments called anthocyanins also form during this process.""",
        
        "classification": """Q: Classify the sentiment: "I loved this movie, it was fantastic!"
A: Positive

Q: Classify the sentiment: "This product broke after one day, very disappointed."
A: Negative""",

        "creative": """Q: Write a short poem about the ocean.
A: The ocean breathes in waves of blue,
Whispering secrets old and true.
It holds the sky within its arms,
And guards the world with ancient calm.

Q: Write a one-paragraph story about a lost key.
A: Maya found the key wedged beneath the old oak floorboard, rusted and forgotten, exactly where her grandmother said it would be. She turned it over in her palm, wondering what door it had once opened — and whether that door still existed at all.""",
        
        "reasoning": """Q: Solve this equation: 5x^2+5x+3=13
A: 5x^2+5x+3-13=0 (subtracting 13 from both sides)
5x^2+5x-10=0
x^2+x-2=0 (dividing both sides by 5)
x^2+2x-x-2=0 (splitting the middle term)
x(x+2)-1(x+2)=0 (taking common factors)
(x-1)(x+2)=0
x-1=0 and x+2=0
x=1 and x=-2 are the solutions

Q: A train leaves Delhi at 3:00 PM traveling at 60 km/h. Another train leaves the same station at 4:00 PM traveling at 90 km/h in the same direction. At what time does the second train catch up to the first?
A: By 4:00 PM, the first train has already traveled for 1 hour at 60 km/h, so it has a 60 km head start.
The second train gains on the first at a rate of 90 - 60 = 30 km/h (the difference in their speeds).
To close a 60 km gap at a gain rate of 30 km/h, it takes 60 ÷ 30 = 2 hours.
Since the second train starts at 4:00 PM, it catches up 2 hours later, at 6:00 PM.

Q: A plant kept in a dark closet for two weeks has yellow, wilted leaves, even though it was watered regularly. What is the most likely explanation?
A: Since the plant was watered regularly, dehydration is unlikely to be the cause. The key detail is that it was kept in a dark closet — plants need light for photosynthesis, the process that produces chlorophyll (the pigment that makes leaves green) and provides the plant's energy. Without light, the plant cannot photosynthesize, causing chlorophyll to break down and the energy-starved plant to wilt. The most likely explanation is lack of sunlight, not lack of water.""",
        "summarization": """Q: Summarize this paragraph:
The Great Barrier Reef, located off the coast of Queensland, Australia,
is the world's largest coral reef system, stretching over 2,300 kilometers.
It is home to thousands of species of marine life, including fish, sharks,
turtles, and countless types of coral. In recent decades, rising ocean
temperatures have caused repeated mass bleaching events, where corals lose
the algae that give them color and nutrients, often leading to coral death.
Scientists warn that without significant reductions in global carbon
emissions, much of the reef could be lost within the coming decades.

A: The Great Barrier Reef is the world's largest coral reef system, home to
diverse marine life. Rising ocean temperatures have caused repeated coral
bleaching, and scientists warn the reef could be largely lost without major
cuts to carbon emissions.

Q: Summarize this paragraph:
Remote work became widespread during the COVID-19 pandemic as companies
sought to keep employees safe while maintaining operations. Many businesses
discovered that productivity didn't decline as expected, and some even saw
improvements due to fewer office distractions and flexible schedules.
However, challenges emerged around employee isolation, difficulty
separating work from personal life, and reduced spontaneous collaboration
that often happens in person. As a result, many companies have since
adopted hybrid models, blending remote and in-office work to balance these
tradeoffs.

A: Remote work expanded rapidly during the pandemic and often maintained or
improved productivity, but brought challenges like isolation and reduced
spontaneous collaboration. Many companies have responded by adopting
hybrid work models to balance these tradeoffs."""}
         
    selected_examples = examples[category]
    
    return f"""Here are some examples:
{selected_examples}

Now answer this question in the same style:
Q: {task}
A:"""

def cot_prompt(task):
    return f"""{task}

Think through this carefully before answering. Use whichever of the following steps are genuinely useful for this specific task — skip any step that doesn't add value:
1. Identify exactly what is being asked, if it isn't already obvious.
2. Work through the relevant facts, logic, or calculations needed.
3. Reason through how these pieces connect to reach an answer.
4. State your final conclusion clearly.
5.Structure your answer in a way that is easy to follow, using bullet points or numbered steps  but only if helpful.

Don't over-explain or add unnecessary detail — only include what is genuinely needed to reach the answer."""

def judge_prompt(task, resp1, resp2, resp3):
    return f"""You are a strict, discerning expert evaluator comparing three AI responses to the same task. Your job is to genuinely differentiate quality, not give everyone similar high scores.

Task: {task}
Response A (Zero-shot — no examples or special instructions given): {resp1}

Response B (Few-shot — given example answers to learn the pattern from): {resp2}

Response C (Chain-of-Thought — explicitly asked to reason step by step): {resp3}


Evaluation criteria:
1. Relevance and factual accuracy — does it correctly address the task?
2. Completeness — does it cover what's actually needed, no more, no less?
3. Appropriateness of length — a concise, direct answer that fully satisfies the task is BETTER  and should be rewardedthan a longer one that pads with unnecessary detail which should be penalized. Only reward length when the task genuinely requires depth, multiple steps, or thorough explanation. Penalize responses that are needlessly long without adding value, and penalize responses that are too brief to actually answer what was asked.
4. Clarity and coherence — is it well-structured and easy to understand(should be rewarded), or is it confusing and disorganized(should be penalized)?
5. Reward if the response demonstrates the specific strengths of its prompting technique — for example, does the few-shot response effectively leverage the examples provided, and does the chain-of-thought response show clear step-by-step reasoning
keep in mind:

Important: Evaluate all three responses simultaneously before assigning any scores. 
Do not assess one response, score it, and then move on to the next. 
This is a comparative evaluation, not an absolute one. 
To avoid positional bias (such as favoring the first, second, or third response based on order), compare the strengths and weaknesses of all three responses side by side and use the full set of comparisons when determining the final scores and rankings. 
Ensure that no response receives an advantage or disadvantage simply because of its position in the sequence.

Process:
First, rank the three responses from strongest to weakest based on the criteria above. 
Then assign scores that clearly reflect this relative ordering — the gap between the best and worst response should be meaningful (at least 10-15 points) unless they are genuinely nearly identical in substance. 
Do not default to giving multiple responses the same or near-identical scores unless truly indistinguishable. A perfect score of 100 should be rare, reserved only for a response with no plausible room for improvement
Most good responses should fall in the 65-92 range, with higher scores reserved only for exceptional, clearly superior answers and lower scores than 60 to really poor ones that fail to meet the task requirements in important ways.


After scoring, identify the best technique and explain your reasoning in 1-2 sentences, referencing the specific criteria above that drove your decision."""

def classify_task_prompt(task):
    return f"""Classify the given task into one of the following 5 categories:
1. factual - if asking direct information on something or an explanation of how/why something works
2. classification - if asked to sort, label, or categorize something
3. creative - if it involves writing original content, innovating ideas, imaginary/creative story writing, or generating own ideas
4. reasoning - if it involves problem solving, logic, deep thinking, math, finding reasons and clues
5. summarization - if asked for a conclusion, shortening of text, extracting key points, or explaining something briefly

Task: {task}"""


def judge_custom_prompt(task, resp1, resp2, resp3, zero_score, few_score, cot_score, custom_prompt,custom_response):
    return f"""You are a strict expert evaluator. A user has written their own custom prompt to answer a task, and you must evaluate how well it performed compared to three established prompting techniques.

Task: {task}

The three established technique responses and their scores (already evaluated):
Response A (Zero-shot, scored {zero_score}/100): {resp1}
Response B (Few-shot, scored {few_score}/100): {resp2}
Response C (Chain-of-Thought, scored {cot_score}/100): {resp3}

The user's custom prompt and its response (not yet scored):
Custom Prompt: {custom_prompt}
Response D : {custom_response}

Dvide scoring in two parts 83 points for the quality of the response itself, and 17 points for the quality of the user's prompt .

RESPONSE SCORING: OUT OF 83 POINTS, score Response D on the following criteria:
Using the existing scores as your calibration baseline(scale them out of 83 instead of 100), score Response D on the same criteria:
11. Relevance and factual accuracy — does it correctly address the task?
2. Completeness — does it cover what's actually needed, no more, no less?
3. Appropriateness of length — a concise, direct answer that fully satisfies the task is BETTER  and should be rewardedthan a longer one that pads with unnecessary detail which should be penalized. Only reward length when the task genuinely requires depth, multiple steps, or thorough explanation. Penalize responses that are needlessly long without adding value, and penalize responses that are too brief to actually answer what was asked.
4. Clarity and coherence — is it well-structured and easy to understand(should be rewarded), or is it confusing and disorganized(should be penalized)?
Note:Following process is the evaluation process followed by other judges on other 3 responses, so take this process as a baseline to calibrate your scoring of Response D.
Process:First, rank the three responses from strongest to weakest based on the criteria above. 
Then assign scores that clearly reflect this relative ordering — the gap between the best and worst response should be meaningful (at least 10-15 points) unless they are genuinely nearly identical in substance. 
Do not default to giving multiple responses the same or near-identical scores unless truly indistinguishable. A perfect score of 100 should be rare, reserved only for a response with no plausible room for improvement
Most good responses should fall in the 65-92 range, with higher scores reserved only for exceptional, clearly superior answers and lower scores than 60 to really poor ones that fail to meet the task requirements in important ways.


PROMPT SCORING:OUT OF 17 POINTS, score the user's prompt on the following criteria:
Reward prompts that:
Clearly communicate the objective
Specify useful constraints or formatting
Reduce ambiguity
Include helpful examples or structure
Improve answer quality in a meaningful way


Penalize prompts that:
Are vague or underspecified
Include contradictory instructions
Add unnecessary complexity
Contain irrelevant directions
Fail to guide the model effectively

Calculate the scores for Response D and the user's prompt, and provide a final custom_score out of 100.
If user custom_score scores higher than all three established techniques, acknowledge this explicitly and identify what made the user's prompt effective. If it scores lower, explain specifically what the user's prompt lacked or could improve.

Identify which of the four responses (zero_shot, few_shot, cot, or custom)according to final marks, performed best overall."""