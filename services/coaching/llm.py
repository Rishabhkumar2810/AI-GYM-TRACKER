from services.config.workout_config import PROMPT


class LLMCoach:
    def __init__(self, groq_client):
        self.client = groq_client
        self.history = []
        self.system_prompt = PROMPT
        self.last_error = None

    def give_feedback(self, event, issue):
        prompt = f"Event: {event}"

        if issue:
            prompt += f" Form Issue: {issue}"

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history[-10:],
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.client.chat.completions.create(
               model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.4,
            )

            
            text = None
            try:
                text = response.choices[0].message.content.strip()
            except Exception:
                # Last-resort: try to coerce to string
                try:
                    text = str(response)
                except Exception:
                    text = None

        except Exception as e:
            import logging
            logging.exception("LLM request failed")
            # Store a short error message for UI diagnostics (no secrets)
            try:
                self.last_error = str(e)
            except Exception:
                self.last_error = "Unknown LLM error"
            text = "Sorry, the coach is unavailable right now."

        text = (text or "").strip()
        if not text:
            text = "Sorry, the coach is unavailable right now."

        self.history.append({"role": "assistant", "content": text})

        return text
    