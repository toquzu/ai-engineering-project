
.PHONY: install run evaluate analyze test clean

install:
	py -m pip install -r requirements.txt

run:
	py src/main.py

evaluate:
	py src/evaluate.py

analyze:
	py src/analyze_errors.py

test:
	py src/test_retry.py
	py src/test_anthropic_retry.py

clean:
	py -c "from pathlib import Path; p=Path('results'); [f.unlink() for f in p.glob('*.jsonl') if f.is_file()]"
