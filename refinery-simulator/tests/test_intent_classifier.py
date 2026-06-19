import pytest
from chatbot.intent_classifier import detect_intent, INTENT_KNOWLEDGE, INTENT_CURRENT, INTENT_ANALYSIS, INTENT_SIMULATION


def test_detect_knowledge():
    assert detect_intent("What is FCC?") == INTENT_KNOWLEDGE
    assert detect_intent("What's a hydrotreater") == INTENT_KNOWLEDGE
    assert detect_intent("Why is hydrotreater used?") == INTENT_KNOWLEDGE


def test_detect_current():
    assert detect_intent("Show current CDU flow rate") == INTENT_CURRENT
    assert detect_intent("What is the CDU flow rate today?") == INTENT_CURRENT
    assert detect_intent("Which unit has highest throughput?") == INTENT_CURRENT
    assert detect_intent("What is current CDU flow rate") == INTENT_CURRENT


def test_detect_analysis():
    assert detect_intent("Why is FCC yield decreasing?") == INTENT_ANALYSIS
    assert detect_intent("What is causing the pressure rise?") == INTENT_ANALYSIS
    assert detect_intent("Why is CDU pressure increasing?") == INTENT_ANALYSIS


def test_detect_simulation():
    assert detect_intent("If CDU flow becomes 6000, what should temperature be?") == INTENT_SIMULATION
    assert detect_intent("What if FCC temperature decreases by 20C?") == INTENT_SIMULATION
    assert detect_intent("If hydrotreater sulfur feed doubles") == INTENT_SIMULATION
    assert detect_intent("If CDU flow becomes 6000") == INTENT_SIMULATION
    assert detect_intent("If FCC feed increases by 20%") == INTENT_SIMULATION
    assert detect_intent("If sulfur content doubles") == INTENT_SIMULATION


def test_validation_twenty_simulation_questions():
    questions = [
        "If CDU flow rate increases from its current value to 6000 BPD, what operating parameter adjustments will be required?",
        "Current FCC temperature is 1003°C and yield is 82.34%. If feed rate increases by another 20%, what will be the operational impact?",
        "Suppose the hydrotreater pressure drops to 40 bar, what will happen?",
        "Assume the sulfur content in CDU feed doubles, what adjustments are required?",
        "What will happen if we decrease the FCC catalyst circulation rate?",
        "What changes are required if the target yield for diesel is set to 45%?",
        "What should happen if the cooling water temperature increases by 5 degrees?",
        "What adjustments are required if CDU throughput reaches 7000 BPD?",
        "What is the consequence of increasing FCC feed rate by another 10%?",
        "If the reboiler duty decreases by 15%, what is the operational impact?",
        "Suppose we increase the reflux ratio in the fractionator, what is the consequence?",
        "Under what scenario would we need to recommend a shutdown of the CDU?",
        "If the feed rate increases, what is the risk of catalyst deactivation?",
        "What adjustments are required to achieve the target purity?",
        "Recommend optimal operating parameters if we assume a 5% increase in crude density.",
        "If we increase the feed temperature, what changes are required in the condenser?",
        "Suppose the diesel draw rate decreases, what will happen to the storage levels?",
        "If we decrease the naphtha endpoint, what is the impact on octane number?",
        "Under this scenario, what changes are required for the hydrotreater?",
        "What is the risk if the pressure increases beyond 50 bar?"
    ]
    for q in questions:
        assert detect_intent(q) == INTENT_SIMULATION, f"Failed to classify as SIMULATION: {q}"
