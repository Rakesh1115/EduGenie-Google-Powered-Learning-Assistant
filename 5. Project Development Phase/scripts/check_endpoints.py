from fastapi.testclient import TestClient
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.main import app

# Monkeypatch the gemini service get_gemini_service to avoid external calls
import app.services.gemini_service as gemini_mod

class DummyService:
    def generate(self, prompt: str, **kwargs):
        # Return a simple markdown depending on prompt keywords
        if 'quiz' in prompt.lower():
            return "1. What is 2+2?\nA. 3\nB. 4\nC. 5\nD. 6\nAnswer: B\nExplanation: 2+2=4"
        if 'summar' in prompt.lower():
            return "# Title\nThis is a short summary.\n- takeaway 1\n- takeaway 2"
        if 'roadmap' in prompt.lower():
            return "# Week 1\n- Intro\n# Week 2\n- Build skills"
        if 'explain' in prompt.lower() or 'concept' in prompt.lower():
            return "# Overview\nAn explanation of the topic.\n## Examples\n- example"
        # default QA
        return "# Answer\nThis is a direct answer.\n## Explanation\nDetails"

# Replace factory
gemini_mod._service_instance = DummyService()

def run_checks():
    client = TestClient(app)
    endpoints = [
        ("/qa/", {'question': 'What is photosynthesis?'}),
        ("/explain/", {'topic': 'Photosynthesis', 'level': 'beginner'}),
        ("/quiz/", {'topic': 'Basic math', 'num_questions': 3}),
        ("/summarize/", {'text': 'This is a long text about testing, it should be summarized.'}),
        ("/roadmap/", {'subject': 'Python programming', 'duration_weeks': 4}),
    ]
    for path, payload in endpoints:
        resp = client.post(path, json=payload)
        print(path, '->', resp.status_code)
        try:
            print(resp.json())
        except Exception:
            print(resp.text)

if __name__ == '__main__':
    run_checks()
