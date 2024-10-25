# AI Assistant for Cephalgia, Headaches, and Migraines

This project is a comprehensive AI-powered assistant designed to help medical professionals and researchers in the field of cephalgia, headaches, and migraines. It uses OpenAI's GPT models and various tools to provide information, answer questions, and process audio inputs.

## Project Structure

- `app/`: Main application directory
  - `api/`: API endpoints
  - `core/`: Core functionality and settings
  - `services/`: Various services (OpenAI, Audio, etc.)
- `frontend/`: Gradio interface
- `ui_config_pt_br.yaml`: UI configuration file in Brazilian Portuguese

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   - `OPENAI_NEUROCURSO_API_KEY`: Your OpenAI API key
4. Run the FastAPI backend: `uvicorn app.main:app --reload`
5. Run the Gradio frontend: `python frontend/gradio_app.py`

## Features

The application provides a Gradio interface with several tabs, each offering different functionalities:

### 1. Create Assistant

This tab allows you to create a new AI assistant.

- Fill in the required fields:
  - Name
  - Model (select from dropdown)
  - Instructions/Prompt
  - Description
  - User ID
- Adjust Temperature and Top P values if needed
- Click "Create Assistant" to generate a new assistant

### 2. Send Question

Use this tab to send questions to an existing assistant.

- Provide the Assistant ID
- Enter your question
- Specify User ID and Thread ID (if applicable)
- Click "Send" to get a response

### 3. Audio Question

This tab enables you to ask questions using voice input.

- Provide the Assistant ID
- Record your question using the microphone
- The recorded audio will be transcribed and sent to the assistant
- The response will be displayed as text and also converted to speech

### 4. Create/Update Vector Store

This tab is used to manage the vector store for document retrieval.

- Enter the Assistant ID
- Upload files or provide file paths
- Click "Create/Update" to process the documents

### 5. List Assistants

Use this tab to view all created assistants.

- Click "List" to see all available assistants

## API Endpoints

The backend provides several API endpoints:

python:app/main.py
startLine: 40
endLine: 45


These endpoints handle various functionalities such as managing assistants, vector stores, threads, questions, and audio processing.

## Configuration

The project uses a YAML configuration file (`ui_config_pt_br.yaml`) for UI labels and settings. You can modify this file to change the language or adjust UI elements. The configuration includes settings for models, API base URL, and various UI labels.

## Audio Processing

The application supports audio input and output. It uses OpenAI's Whisper model for speech-to-text and a text-to-speech service for generating audio responses.


python:app/api/api_v1/endpoints/question_audio.py
startLine: 16
endLine: 36

## Assistant Creation and Management

Assistants are created using OpenAI's API. The project includes functionality to create, retrieve, and manage assistants:


## Vector Store and File Search

The project implements vector store functionality for efficient document retrieval. It uses OpenAI's file search capabilities:



## Prompt Engineering

The assistant uses carefully crafted prompts to ensure accurate and relevant responses:


python:app/core/asst/prompt_cefaleias_v02.py
startLine: 8
endLine: 23


## Tips for Use

1. When creating an assistant, provide clear and specific instructions for best results.
2. For audio questions, ensure you're in a quiet environment for accurate transcription.
3. When using the vector store, organize your documents well for efficient retrieval.
4. Use specific and well-formulated questions to get the most accurate responses.
5. Regularly update the vector store with new relevant documents to keep the assistant's knowledge current.

## Limitations

- The assistant's knowledge is based on its training data and the documents you provide.
- Audio transcription and text-to-speech quality may vary depending on input quality and accent.
- The system is designed for medical professionals and may not be suitable for general public use without proper context.

## Future Improvements

- Implement user authentication and session management for personalized experiences.
- Enhance error handling and provide more detailed feedback to users.
- Optimize vector store for faster document retrieval and more accurate context matching.
- Implement a feedback system for continuous improvement of the assistant's responses.
- Expand language support beyond Brazilian Portuguese.

## Contributing

Contributions to this project are welcome. Please ensure you follow the coding standards and submit pull requests for any new features or bug fixes.

## License

[Specify your license here]

For any issues, suggestions, or questions, please open an issue in the project repository or contact the maintainers.