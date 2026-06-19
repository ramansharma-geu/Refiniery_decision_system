Refinery Chatbot Manual Validation Suite

Purpose
-------
This manual validation suite helps a human reviewer check the chatbot's answer quality across the four pipelines: KNOWLEDGE, CURRENT_DATA, ANALYSIS, and SIMULATION. Each question lists the expected structure, forbidden phrases, word limit, and pass/fail checks.

How to use
----------
1. Start the local app or call the function `get_hybrid_chatbot_response(user_query, slm_service)` with a DummySLM or real SLM.
2. For CURRENT_DATA questions ensure the database has realistic latest records for units (CDU, FCC, VDU, Hydrotreater, Storage Terminal).
3. Check each response against the expected sections and quality checks below.

Global Quality Rules
--------------------
- Direct answer sentence first (first line).
- Max 5 bullets for KNOWLEDGE responses.
- Max 8 bullets total for ANALYSIS and SIMULATION outputs.
- Responses should be <= 150 words when possible.
- Reject responses containing any of these phrases (case-insensitive):
  - "The operational significance"
  - "This suggests"
  - "It is important to note"
  - "Based on available information"
  - "Further analysis may be required"
  - "Data unavailable"
  - "Cannot determine"

Scoring
-------
- Pass: All structural expectations met and forbidden phrases absent.
- Warning: Minor violations (extra bullet, slightly long sentence) but still useful.
- Fail: Contains a forbidden phrase, long theory intro, or returns only raw DB rows for non-CURRENT_DATA intents.

KNOWLEDGE QUESTIONS (5)
------------------------
Expectations: direct answer first, then up to 5 short operational bullets, no long theory.

1) What is CDU?
2) What is FCC?
3) What is VDU?
4) Why is hydrotreater used?
5) What causes catalyst deactivation?

Pass criteria for each:
- First line: a one-sentence direct definition or function.
- Up to 5 bullets: operational notes, control points, monitoring cues, safety flags.
- No long theoretical paragraphs.

CURRENT DATA QUESTIONS (5)
---------------------------
Expectations: Read-only database query responses. No AI synthesis or invented data.

1) Show CDU flow rate.
2) Show FCC temperature.
3) Which unit has highest throughput?
4) Which unit has maximum downtime?
5) Show hydrotreater pressure.

Pass criteria for each:
- Response pulls values from DB latest records.
- No model explanation, conclusions, or invented numbers.
- Includes timestamp when available.

ANALYSIS QUESTIONS (5)
----------------------
Expectations: LLM synthesizes from DB-supplied current values and delivers three sections: Current Values, Possible Causes, Recommendations.

1) Why is FCC yield decreasing?
2) Why is CDU pressure increasing?
3) Why is energy consumption rising?
4) Why is throughput decreasing?
5) What can cause hydrotreater shutdown?

Required format:
- Line 1: Direct conclusion sentence.
- Section: "Current Values" with per-unit numeric bullets.
- Section: "Possible Causes" with up to 3 bullets.
- Section: "Recommendations" with up to 2 bullets.

SIMULATION QUESTIONS (7+)
-------------------------
Expectations: Rules engine estimates parameters, then LLM explains in four sections: Recommended Parameters, Consequences, Operational Risks, Recommendations.

1) If CDU flow becomes 6000 BPD, what should temperature be?
2) If CDU flow becomes 8000 BPD, what are the risks?
3) If FCC temperature drops by 20°C, what happens to gasoline yield?
4) If FCC feed increases by 15%, what parameters should change?
5) If VDU vacuum pressure rises, what are the consequences?
6) If hydrotreater sulfur feed doubles, what operating changes are required?
7) If storage terminal utilization reaches 95%, what are the operational risks?

Required format:
- Line 1: Direct recommended parameters sentence.
- Sections: "Recommended Parameters", "Consequences", "Operational Risks", "Recommendations".
- Max 8 bullets total.

Example pass/fail checklist (per question)
-----------------------------------------
- Direct sentence?  Y/N
- Required sections present?  Y/N
- Forbidden phrases present?  Y/N -> FAIL if any
- Word count <= 150?  Y/N
- DB-only for current-data? Y/N

Notes
-----
- For CURRENT_DATA tests, load realistic last-known records using `refinery-simulator/generate_seed_data.py` or `seed_data.sql`.
- This manual suite is the source of truth for a later automation harness that can call the chatbot and assert structural rules.

Contact
-------
If you'd like, I can also generate an automated runner that executes these queries against a mocked DB and a Dummy SLM and produces a pass/fail report.
