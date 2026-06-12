import requests
import re
import json

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
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False
        }
        if context_data:
            payload["system"] = f"You are a helpful refinery decision intelligence system. Here is the relevant operational context data: {json.dumps(context_data)}"
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get("response", "No response content from Ollama.")
            else:
                return f"Ollama error: HTTP {response.status_code}. Falling back to domain knowledge base.\n" + self._query_mock(prompt, context_data)
        except Exception as e:
            return f"Ollama connection failed ({e}). Falling back to domain knowledge base.\n" + self._query_mock(prompt, context_data)

    def _query_huggingface(self, prompt, context_data):
        try:
            from transformers import pipeline
            if not self._hf_pipeline:
                if not self.hf_model_path:
                    self.hf_model_path = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
                self._hf_pipeline = pipeline("text-generation", model=self.hf_model_path, device_map="auto")
            
            system_prompt = "You are a refinery decision assistant. Synthesize the operational question."
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
        
        # 1. Base Domain Knowledge Answers
        knowledge_base = {
            "what is cdu": "The Crude Distillation Unit (CDU) is the primary fractional distillation column of a refinery. It operates at atmospheric pressure to separate crude oil into fractions based on boiling points. The output includes Light Naphtha, Heavy Naphtha, Kerosene, Light Gas Oil, and Atmospheric Residue (which serves as feed to the VDU).",
            "what is vdu": "The Vacuum Distillation Unit (VDU) processes the heavy Atmospheric Residue from the CDU. By operating under deep vacuum (0.5 to 1.5 psi absolute), it lowers boiling points and separates high-boiling heavy hydrocarbons into Vacuum Gas Oils (VGO) and Vacuum Residue without causing thermal cracking (which occurs above 800°F).",
            "what is fcc": "The Fluid Catalytic Cracking (FCC) Unit is a crucial conversion system. It uses a circulating fluidized bed of catalyst (zeolite) at high temperatures (950°F to 1050°F) to crack long-chain heavy gas oils (VGO) from the VDU into high-octane gasoline, light diesel fractions, and Liquefied Petroleum Gases (LPG).",
            "what is hydrotreater": "The Hydrotreater Unit removes sulfur, nitrogen, and other impurities from oil fractions (like naphtha, diesel, or jet fuel). It operates at high temperatures (600°F-700°F) and pressures (600-1000 psi) in the presence of hydrogen and a catalyst. This is critical for meeting environmental standards and preventing poisoning of downstream catalysts.",
            "what is storage terminal": "The Storage Terminal manages crude feedstock inventory and holds finished fuels prior to distribution. It serves as a buffer system between process units, ensuring feedstock continuity and logging terminal shipping lines.",
            "what is throughput": "Throughput is the rate at which crude oil or process intermediate streams are charged (processed) in a unit, typically measured in barrels per day (bbl/day) or barrels per hour (bbl/hr). Keeping throughput high optimizes revenue but stresses thermal and mechanical design limits.",
            "what is yield": "Yield is the percentage of finished, high-value liquid products recovered relative to the total raw feedstock volume. For example, FCC yield is the percentage of gasoline and LPG recovered from gas oil feed. Higher yield means better process efficiency.",
            "what is pressure": "Pressure represents the force per unit area within columns, pipes, and reactors, measured in psi or bar. Elevated pressures are required in hydrotreaters to maintain hydrogen solubility, but in units like the CDU or FCC, pressure increases indicate fouling, loading stresses, or potential relief valve risks.",
            "what is temperature": "Temperature is the thermal index of process fluids. High temperatures are required to heat crude in furnaces or crack bonds in the FCC. Monitoring temperatures ensures precise fractional boiling and prevents equipment metallurgy failure.",
            "what is energy consumption": "Energy consumption tracks the utilities (fuel gas, steam, power) consumed to pump and heat process streams. Minimizing energy consumption improves refining margins and complies with carbon emission audits.",
            "refinery bottlenecks": "Refinery bottlenecks occur when hydraulic limits (flooding in trays, pump capacities), thermal limits (heater duties), or catalyst limits prevent throughput increases. In RDIS, the Hydrotreater has a design capacity limit of 25,000 bbl/day, which acts as a primary operational bottleneck when throughput increases by 10%.",
            "delayed maintenance": "Delayed maintenance increases the operational risk index. By postponing inspections on high-temperature, high-pressure equipment like the CDU, the probability of micro-cracks, fouling, or tube ruptures increases. This shows up as higher downtime hours due to emergency repairs."
        }

        # Scan for direct matching keys in the prompt
        for key, text in knowledge_base.items():
            if key in prompt_clean:
                # If we have database context, combine it for a hybrid response!
                if context_data:
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
