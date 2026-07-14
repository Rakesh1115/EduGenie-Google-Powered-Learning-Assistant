from typing import Any, Dict


def format_markdown(response_text: str) -> Dict[str, Any]:
	"""Return a structured JSON payload containing the markdown output and a plain-text fallback."""
	# Minimal processing for now — keep markdown intact and provide a plain text variant
	plain = response_text
	return {"markdown": response_text, "text": plain}


def extract_quiz_items(markdown: str):
	"""Attempt to parse a simple markdown quiz into structured items.

	This is intentionally conservative and returns markdown under 'raw' when parsing fails.
	"""
	items = []
	try:
		lines = [l.strip() for l in markdown.splitlines() if l.strip()]
		cur = None
		for ln in lines:
			if len(ln) > 2 and ln.split('.', 1)[0].isdigit() and ln.split('.', 1)[1].startswith(' '):
				if cur:
					items.append(cur)
				cur = {"question": ln, "choices": [], "answer": None, "explanation": None}
			elif ln.startswith("A.") or ln.startswith("B.") or ln.startswith("C.") or ln.startswith("D."):
				if cur is not None:
					cur["choices"].append(ln)
			elif ln.lower().startswith("answer:"):
				if cur is not None:
					cur["answer"] = ln.split(':', 1)[1].strip()
			elif ln.lower().startswith("explanation:"):
				if cur is not None:
					cur["explanation"] = ln.split(':', 1)[1].strip()
		if cur:
			items.append(cur)
		return {"items": items, "raw": markdown}
	except Exception:
		return {"items": [], "raw": markdown}

