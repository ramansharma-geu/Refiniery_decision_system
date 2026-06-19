import requests
import re
import json

SYSTEM_INSTRUCTIONS = (
    "You are a Senior Refinery Process Engineer with 25+ years of hands-on refinery experience.\n"
    "Rules:\n"
    "1. Answer refinery questions only.\n"
    "2. Detect abnormal values and flag them as Observed Concern.\n"
    "3. Prioritize likely causes (Most Likely Cause vs Other Possible Causes).\n"
    "4. Recommend safe and practical operational actions.\n"
    "5. Think like a refinery operations engineer. No generic AI explanations.\n"
    "6. Give direct answer first (one short sentence).\n"
    "7. Use bullet points for details.\n"
    "8. Be extremely concise. Max 130 words for analysis, 120 words for simulations, 100 words otherwise.\n"
    "9. No theory unless requested.\n"
    "10. No AI-style introductions or disclaimers.\n"
    "11. Focus on CDU, VDU, FCC, Hydrotreater and Storage Terminal operations.\n"
    "12. Never output 'Analysis:', 'Economic Impact:', or 'Confidence Level:' sections unless explicitly asked.\n"
    "13. Use engineer-style short operational language. Max 120 words for simulation responses.\n"
    "Forbidden phrases: 'The operational significance is', 'This indicates', 'Based on available information', 'Data may require further analysis', 'This suggests', 'It is important to note'.\n"
)

class SLMService:
    def __init__(self, provider='mock', ollama_url='http://localhost:11434/api/generate', ollama_model='qwen2.5:1.5b', hf_model_path=None):
        self.provider = provider
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model
        self.hf_model_path = hf_model_path
        self._hf_pipeline = None

    def query(self, prompt, context_data=None):
        """
        Queries the SLM based on the configured provider.
        """
        if self.provider == 'ollama':
            return self._query_ollama(prompt, context_data)
        elif self.provider == 'huggingface':
            return self._query_huggingface(prompt, context_data)
        else:
            return self._query_mock(prompt, context_data)

    def _query_ollama(self, prompt, context_data):
        # Build a single coherent prompt that includes system instructions, optional context data,
        # and the user-level prompt. We explicitly instruct the model how to treat database facts.
        system_prompt = SYSTEM_INSTRUCTIONS
        context_block = ""
        if context_data:
            # Keep context compact — only include keys and numeric values to avoid verbosity
            try:
                compact = {k: v for k, v in context_data.items()}
                context_block = f"\n\n[DATABASE CONTEXT — USE ONLY AS FACTS]: {json.dumps(compact)}"
            except Exception:
                context_block = "\n\n[DATABASE CONTEXT — UNAVAILABLE OR TOO LARGE]"

        # Dynamically select word count and formatting rules to prevent contradictory instructions
        if "Observed Concerns" in prompt or "Possible Causes" in prompt:
            word_limit = 130
            rules = (
                "- Start with a single-line direct engineering conclusion (one short sentence).\n"
                "- Write the exact section headers: Current Values, Observed Concerns, Possible Causes, Operational Impact, Recommendations, Confidence Level.\n"
                "- Possible Causes header MUST list 'Most Likely Cause' and 'Other Possible Causes' subheadings.\n"
                "- Be extremely concise and keep the entire response under 130 words."
            )
        elif "Current Conditions" in prompt and "Target Conditions" in prompt:
            word_limit = 120
            rules = (
                "- Start with a single-line direct engineering conclusion (one short sentence).\n"
                "- Write the exact section headers: Current Conditions, Target Conditions, Parameter Adjustments, Expected Changes, Operational Risks, Recommendations.\n"
                "- Do NOT include Economic Impact or Confidence Level sections unless explicitly asked.\n"
                "- Be extremely concise and keep the entire response under 120 words."
            )
        else:
            word_limit = 100
            rules = (
                "- Start with a single-line direct answer (one short sentence).\n"
                "- Then provide bullets (max 4 total).\n"
                "- Be concise, practical, and focus on operational decisions.\n"
                "- Keep the entire response under 100 words."
            )

        full_prompt = (
            f"{system_prompt}\n\nUser question:\n{prompt}\n\nENFORCE THE FOLLOWING FORMAT:\n"
            f"{rules}\n"
            "- Do NOT include introductions, conversational filler, disclaimers, or any forbidden phrases.\n"
            f"{context_block}\n\nAnswer now:"
        )

        payload = {
            "model": self.ollama_model,
            "prompt": full_prompt,
            "stream": False
        }

        # Validator-powered re-prompt loop: if response doesn't pass quality checks, retry up to 2 times
        from response_validator import validate_response
        max_attempts = 2
        attempt = 0
        last_good_text = None
        last_details = None
        while attempt <= max_attempts:
            attempt += 1
            try:
                response = requests.post(self.ollama_url, json=payload, timeout=30)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # extract text similar to before
                        text = None
                        for k in ("response", "text", "result", "output"):
                            if k in data:
                                text = data[k]
                                break
                        if text is None and isinstance(data.get("choices"), list):
                            texts = []
                            for c in data.get("choices"):
                                if isinstance(c, dict):
                                    texts.append(c.get("text") or c.get("message") or "")
                            text = "\n".join([t for t in texts if t]) or json.dumps(data)
                        if text is None:
                            text = json.dumps(data)
                    except ValueError:
                        text = response.text

                    # Validate
                    required_sections = None
                    max_words = 100
                    # Heuristics: if prompt asks for "Current Values" or "Recommendations" enforce those sections
                    if "Current Values" in full_prompt and "Possible Causes" in full_prompt:
                        required_sections = [
                            "Current Values",
                            "Observed Concerns",
                            "Possible Causes",
                            "Operational Impact",
                            "Recommendations",
                            "Confidence Level"
                        ]
                        max_words = 130
                    elif "Current Conditions" in full_prompt and "Target Conditions" in full_prompt:
                        required_sections = [
                            "Current Conditions",
                            "Target Conditions",
                            "Parameter Adjustments",
                            "Expected Changes",
                            "Operational Risks",
                            "Recommendations"
                        ]
                        max_words = 120

                    passed, details = validate_response(text, required_sections=required_sections, max_words=max_words)
                    last_good_text = text
                    last_details = details
                    if passed:
                        return text
                    else:
                        # Build a highly detailed, targeted correction hint for Qwen (reflective prompting)
                        feedback_parts = []
                        if not details.get('forbidden_ok'):
                            feedback_parts.append(f"Remove forbidden phrases: {details.get('forbidden_found')}.")
                        if not details.get('word_count_ok'):
                            feedback_parts.append(f"Shorten the answer drastically. It has {details.get('word_count')} words. Keep the entire response under {max_words} words.")
                        if not details.get('sections_ok'):
                            feedback_parts.append(f"Include the required section headers exactly as written: {details.get('sections_missing')}.")
                        if not details.get('bullets_present'):
                            feedback_parts.append("Format details as bullet points (use • or -).")
                        
                        feedback_str = " ".join(feedback_parts)
                        hint = f"\n\n[CRITICAL RETRY CORRECTION]: Your previous response failed safety/formatting validation checks. Required fixes: {feedback_str} Please output the corrected response now, starting with a direct answer and using the exact headers."
                        payload['prompt'] = full_prompt + hint
                        # fallthrough to next attempt
                else:
                    # non-200: log internally and fallback to mock
                    print(f"Ollama returned non-200 status code: {response.status_code}. Falling back to domain mock.")
                    last_good_text = None
                    break
            except Exception as e:
                print(f"Ollama connection error: {e}. Falling back to domain mock.")
                last_good_text = None
                break

        # If we exhaust attempts, return the last text (or fallback mock)
        if last_good_text:
            return last_good_text

        return self._query_mock(prompt, context_data)


    def _query_huggingface(self, prompt, context_data):
        try:
            from transformers import pipeline
            if not self._hf_pipeline:
                if not self.hf_model_path:
                    self.hf_model_path = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
                self._hf_pipeline = pipeline("text-generation", model=self.hf_model_path, device_map="auto")
            
            system_prompt = SYSTEM_INSTRUCTIONS
            if context_data:
                system_prompt += f" Context data: {json.dumps(context_data)}"
                
            full_prompt = f"<|system|>\n{system_prompt}</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
            outputs = self._hf_pipeline(full_prompt, max_new_tokens=250, num_return_sequences=1, temperature=0.7)
            generated_text = outputs[0]["generated_text"]
            # Extract assistant portion
            if "<|assistant|>\n" in generated_text:
                return generated_text.split("<|assistant|>\n")[-1].strip()
            return generated_text
        except Exception as e:
            return f"HuggingFace pipeline failed to load: {e}. Falling back to domain knowledge base.\n" + self._query_mock(prompt, context_data)

    def _query_mock(self, prompt, context_data):
        """
        High-fidelity Mock SLM. Uses matching heuristics to return extremely detailed,
        professionally styled chemical engineering reasoning.
        """
        prompt_clean = prompt.lower()

        # Handle ground truth facts if present in the prompt (RAG / Retrieval dynamic mock generation)
        if "ground truth facts" in prompt_clean:
            lines = prompt.split('\n')
            facts = []
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.startswith('- '):
                    facts.append(line_stripped[2:])
            if facts:
                # Deduce a professional direct answer based on unit keyword
                if "fcc" in prompt_clean:
                    direct_ans = "Fluid Catalytic Cracking (FCC) is a catalytic conversion process that cracks heavy vacuum gas oil feedstocks into high-value light products."
                elif "hydrotreater" in prompt_clean or "hydrotreating" in prompt_clean:
                    direct_ans = "A hydrotreater is a catalytic purification unit that uses hydrogen to remove sulfur and other impurities from refinery streams."
                elif "cdu" in prompt_clean or "crude distillation" in prompt_clean:
                    direct_ans = "The Crude Distillation Unit (CDU) performs atmospheric fractional distillation to separate raw crude oil into boiling-point fractions."
                elif "vdu" in prompt_clean or "vacuum distillation" in prompt_clean:
                    direct_ans = "The Vacuum Distillation Unit (VDU) distills atmospheric residue under deep vacuum to extract vacuum gas oils without thermal cracking."
                elif "storage terminal" in prompt_clean or "storage" in prompt_clean:
                    direct_ans = "The Storage Terminal provides inventory buffering and blending facilities for feedstock continuity and finished product distribution."
                elif "catalyst deactivation" in prompt_clean or "catalyst" in prompt_clean:
                    direct_ans = "Catalyst deactivation is the loss of catalytic activity and selectivity over time due to operational, thermal, and chemical mechanisms."
                else:
                    direct_ans = "Refinery operations analysis indicates the following grounded operational facts."

                # Construct dynamic mock response matching format guidelines
                bullets = [f"• {f}" for f in facts]
                if len(bullets) > 4:
                    bullets = bullets[:4]
                return f"{direct_ans}\n\n" + "\n".join(bullets)
        
        # 1. Base Domain Knowledge Answers
        knowledge_base = {
            "what is cdu": "The Crude Distillation Unit (CDU) is the primary fractional distillation column of a refinery. It operates at atmospheric pressure to separate crude oil into fractions based on boiling points. The output includes Light Naphtha, Heavy Naphtha, Kerosene, Light Gas Oil, and Atmospheric Residue (which serves as feed to the VDU).",
            "what is vdu": "The Vacuum Distillation Unit (VDU) processes the heavy Atmospheric Residue from the CDU. By operating under deep vacuum (0.5 to 1.5 psi absolute), it lowers boiling points and separates high-boiling heavy hydrocarbons into Vacuum Gas Oils (VGO) and Vacuum Residue without causing thermal cracking (which occurs above 800°F).",
            "what is fcc": "Fluid Catalytic Cracking (FCC) cracks heavy vacuum gas oil (VGO) feedstocks into gasoline, light cycle oil (LCO), and LPG using a circulating fluidized zeolite catalyst bed. It does not extract aromatics from heavy fuel oil.",
            "what is hydrotreater": "The Hydrotreater reacts hydrocarbon fractions with hydrogen over a catalyst to remove sulfur, nitrogen, and metals. It does not remove water from crude oil, which is done by the desalter.",
            "what is storage terminal": "The Storage Terminal manages crude feedstock inventory and holds finished fuels prior to distribution. It serves as a buffer system between process units, ensuring feedstock continuity and logging terminal shipping lines.",
            "what is throughput": "Throughput is the rate at which crude oil or process intermediate streams are charged (processed) in a unit, typically measured in barrels per day (bbl/day) or barrels per hour (bbl/hr). Keeping throughput high optimizes revenue but stresses thermal and mechanical design limits.",
            "what is yield": "Yield is the percentage of finished, high-value liquid products recovered relative to the total raw feedstock volume. For example, FCC yield is the percentage of gasoline and LPG recovered from gas oil feed. Higher yield means better process efficiency.",
            "what is pressure": "Pressure represents the force per unit area within columns, pipes, and reactors, measured in psi or bar. Elevated pressures are required in hydrotreaters to maintain hydrogen solubility, but in units like the CDU or FCC, pressure increases indicate fouling, loading stresses, or potential relief valve risks.",
            "what is temperature": "Temperature is the thermal index of process fluids. High temperatures are required to heat crude in furnaces or crack bonds in the FCC. Monitoring temperatures ensures precise fractional boiling and prevents equipment metallurgy failure.",
            "what is energy consumption": "Energy consumption tracks the utilities (fuel gas, steam, power) consumed to pump and heat process streams. Minimizing energy consumption improves refining margins and complies with carbon emission audits.",
            "refinery bottlenecks": "Refinery bottlenecks occur when hydraulic limits (flooding in trays, pump capacities), thermal limits (heater duties), or catalyst limits prevent throughput increases. In RDIS, the Hydrotreater has a design capacity limit of 25,000 bbl/day, which acts as a primary operational bottleneck when throughput increases by 10%.",
            "delayed maintenance": "Delayed maintenance increases the operational risk index. By postponing inspections on high-temperature, high-pressure equipment like the CDU, the probability of micro-cracks, fouling, or tube ruptures increases. This shows up as higher downtime hours due to emergency repairs.",
            "sulfur": (
                "- **Hydrotreater (HDS Unit):** Heavy loading from 30% sulfur surge requires increasing operating temperature (above 650°F) and hydrogen flow rate to maintain desulfurization efficiency.\n"
                "- **Storage Terminal (STA Unit):** Requires immediate segregation of high-sulfur crude to prevent blending contamination and corrosion risk.\n"
                "- **FCC Unit:** High sulfur in feed poisons zeolite catalysts, dropping gasoline yields by 2-5% and increasing sulfur oxides (SOx) in flue gas.\n"
                "- **CDU / VDU:** Increased hydrogen sulfide (H2S) generation raises high-temperature sulfidic corrosion rates, requiring corrosion inhibitor adjustments.\n"
                "- **Amine / Sulfur Recovery Unit (SRU):** Elevated H2S acid gas load may exceed sulfur recovery capacity (typically limited to design specs), causing a system bottleneck.\n"
                "- **Product Quality:** High sulfur carryover directly impacts ultra-low sulfur diesel (ULSD) pool specification limits (max 10 ppm)."
            )
        }

        # Scan for direct matching keys in the prompt
        for key, text in knowledge_base.items():
            if key in prompt_clean:
                # If we have database context, combine it for a hybrid response!
                if context_data and key in ["what is cdu", "what is vdu", "what is fcc", "what is hydrotreater", "what is storage terminal"]:
                    return self._generate_hybrid_response(key, text, context_data)
                return text

        # 2. Handle Scenario-specific questions if database context is attached
        if context_data:
            # Check if user is asking about specific units
            for code in ["cdu", "vdu", "fcc", "hydrotreater", "storage terminal"]:
                if code in prompt_clean:
                    key = code
                    code_upper = "Storage Terminal" if code == "storage terminal" else code.upper()
                    record = context_data.get(code_upper, {})
                    if record:
                        val_str = ", ".join([f"{k.capitalize()}: {v}" for k, v in record.items() if k != 'timestamp'])
                        desc = knowledge_base.get(f"what is {code}", f"Refinery unit {code_upper}.")
                        return f"According to current database records, {code_upper} is operating at: [{val_str}].\n\nOperational Context: {desc}"

            # General database context summarization
            lines = []
            for code, data in context_data.items():
                lines.append(f"- **{code}**: Throughput is {data.get('throughput')} bbl/day, Yield is {data.get('yield')}%, and Energy is {data.get('energy_consumption')} MMBtu/hr.")
            joined = "\n".join(lines)
            return f"Here is the current operational status retrieved from the database:\n\n{joined}\n\nRefinery overall risk is in nominal range. Let me know if you would like to run a specific simulation scenario to model impacts."

        return "I am the RDIS Decision Intelligence Chatbot. I can answer questions about CDU, VDU, FCC, Hydrotreater, Storage Terminal, and explain operational parameters. Try asking 'What is FCC?' or 'What are the current parameters of CDU?'"

    def _generate_hybrid_response(self, topic_key, topic_explanation, context_data):
        """
        Merges SQLite data points with SLM domain knowledge for a rich hybrid response.
        """
        code_map = {
            "what is cdu": "CDU",
            "what is vdu": "VDU",
            "what is fcc": "FCC",
            "what is hydrotreater": "Hydrotreater",
            "what is storage terminal": "Storage Terminal"
        }
        
        unit_code = code_map.get(topic_key)
        if not unit_code:
            # Default to summarizing overall data if no specific unit maps
            return f"{topic_explanation}\n\n<b>Operational Context:</b> The database shows active units running. Current overall throughput is led by CDU at {context_data.get('CDU', {}).get('throughput', 'N/A')} bbl/day."
            
        unit_data = context_data.get(unit_code)
        if not unit_data:
            return f"{topic_explanation}\n\n<b>Operational Context:</b> No recent database records found for {unit_code}."
            
        tp = unit_data.get("throughput")
        yd = unit_data.get("yield")
        pr = unit_data.get("pressure")
        tm = unit_data.get("temperature")
        dt = unit_data.get("downtime")
        en = unit_data.get("energy_consumption")
        
        response = (
            f"<b>Unit Description:</b> {topic_explanation}\n\n"
            f"<b>Current Database Metrics for {unit_code}:</b>\n"
            f"- Throughput: {tp} bbl/day\n"
            f"- Operating pressure: {pr} psi/bar\n"
            f"- Temperature: {tm} °F\n"
            f"- Yield: {yd}%\n"
            f"- Energy Consumption: {en} MMBtu/hr\n"
            f"- Cumulative downtime: {dt} hours\n\n"
            f"<b>SLM Reasoning Analysis:</b> Given these values, the {unit_code} is running at "
        )
        
        # Add dynamic evaluation based on values
        if unit_code == "Hydrotreater" and tp >= 24000:
            response += f"near-maximum loading ({tp} bbl/day relative to 25k bbl/day limit). The high pressure of {pr} psi confirms high mechanical loading. Catalyst beds must be audited for thermal runaway."
        elif unit_code == "FCC" and tp == 0:
            response += "complete outage. Downstream gasoline yields will drop to zero and VGO feed will backup. Emergency storage logistics must be engaged."
        elif dt > 4.0:
            response += f"reduced utilization due to {dt} hours of downtime. Operators should check maintenance delay thresholds."
        else:
            response += f"normal parameters ({round(tp/1000.0, 1)}k bbl/day). Operations are stable, and energy consumption ({en} MMBtu/hr) is within baseline efficiency targets."
            
        return response
