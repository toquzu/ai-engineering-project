AI Project
Requirements
Python 3.11+

Ollama

Downloaded Language Model

Installation
Bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
Running the Project
First, start Ollama and download the model:

Bash
ollama run llama3.2:3b
Then, run the following command in the main project directory:

Bash
python src\main.py / make run
