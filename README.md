# MindMate-AI-Chatbot

MindMate AI is a locally running AI chatbot developed using Python, Streamlit, Ollama, and SQLite.

It allows users to interact with an AI assistant, maintain conversation history, and manage multiple chats.

## Features

- AI-powered chatbot
- Ollama integration
- Qwen 2.5 3B language model
- SQLite database
- Chat history management
- New conversation option
- Delete conversation option
- Context-aware responses
- Simple Streamlit interface

## Technologies Used

- Python
- Streamlit
- Ollama
- SQLite
- Requests
- Qwen 2.5 3B

## Installation

Install the required packages:

```bash
pip install -r requirements.txt
```

Download the Ollama model:

```bash
ollama pull qwen2.5:3b
```

Start Ollama:

```bash
ollama serve
```

Run the application:

```bash
python -m streamlit run mindmate_short.py
```

Open the application:

```text
http://localhost:8501
```

## Project Structure

```text
MindMate-AI-Chatbot/
│
├── mindmate_short.py
├── requirements.txt
├── README.md
└── mindmate.db
```

Note: The database file is created automatically when the application runs.

## Database

SQLite is used to store conversations and messages.

### Tables

1. chats
2. messages

## AI Model

Qwen 2.5 3B runs locally through Ollama.

## Future Enhancements

- User authentication
- Chat export option
- Dark mode
- Voice interaction
- Improved conversation management

## License

This project is developed for educational and learning purposes.
