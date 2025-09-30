# LLM Playground

A modern, interactive web interface for experimenting with multiple Large Language Model (LLM) providers. This playground supports OpenAI, Anthropic, Google AI, Groq, and Hugging Face models with a clean, responsive UI.

## Features

- 🤖 **Multi-Provider Support**: OpenAI, Anthropic, Google AI, Groq, and Hugging Face
- 🎛️ **Advanced Controls**: Temperature, max tokens, top-p, frequency/presence penalties
- 💬 **Interactive Chat**: Real-time conversations with LLMs
- 🎨 **Modern UI**: Clean, responsive design with dark theme
- ⚙️ **Customizable Settings**: System prompts, stop sequences, and model parameters
- 🔄 **Easy Model Switching**: Quick selection between different models and providers

## Supported Models

### OpenAI
- GPT-4o, GPT-4o Mini
- GPT-4 Turbo, GPT-4
- GPT-3.5 Turbo

### Anthropic
- Claude 3.5 Sonnet
- Claude 3 Opus, Sonnet, Haiku

### Google AI
- Gemini 1.5 Pro, Flash
- Gemini 1.0 Pro

### Groq
- Llama 3.1 (70B, 8B)
- Llama 3 (70B, 8B)
- Mixtral 8x7B
- Gemma 2 (9B, 2B)

### Hugging Face
- Various open-source models via Inference API

## Setup Instructions

### Prerequisites
- Python 3.7+
- API keys for the LLM providers you want to use

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rguntuku8/my-test-llmplayground.git
   cd my-test-llmplayground
   ```

2. **Set up Python environment**
   ```bash
   python -m venv backend_env
   source backend_env/bin/activate  # On Windows: backend_env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and add your API keys:
   ```env
   # Get API keys from the respective provider websites
   GOOGLE_API_KEY=your_google_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GROQ_API_KEY=your_groq_api_key_here
   HF_TOKEN=your_huggingface_token_here
   ```

### Getting API Keys

| Provider | Get API Key | Documentation |
|----------|-------------|---------------|
| **OpenAI** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | [OpenAI API Docs](https://platform.openai.com/docs) |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) | [Anthropic API Docs](https://docs.anthropic.com/) |
| **Google AI** | [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey) | [Google AI Docs](https://ai.google.dev/) |
| **Groq** | [console.groq.com/keys](https://console.groq.com/keys) | [Groq API Docs](https://console.groq.com/docs) |
| **Hugging Face** | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | [HF Inference API](https://huggingface.co/docs/api-inference) |

### Running the Application

1. **Start the backend server**
   ```bash
   python server.py
   ```

2. **Start the frontend server**
   ```bash
   python -m http.server 8000
   ```

3. **Open your browser**
   Navigate to `http://localhost:8000`

## Usage

1. **Select a Model**: Choose from the dropdown menu in the top-left
2. **Configure Settings**: Adjust temperature, max tokens, and other parameters
3. **Set System Prompt**: Define the AI's behavior and context (optional)
4. **Start Chatting**: Type your message and press Enter or click Send

### Advanced Features

- **Temperature**: Controls randomness (0.0 = deterministic, 1.0 = creative)
- **Max Tokens**: Limits response length
- **Top-p**: Nucleus sampling parameter
- **Frequency/Presence Penalty**: Reduces repetition
- **Stop Sequences**: Custom stopping conditions
- **System Prompt**: Sets AI behavior and context

## Project Structure

```
my-test-llmplayground/
├── index.html          # Frontend interface
├── styles.css          # UI styling
├── script.js           # Frontend logic
├── server.py           # Flask backend server
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── models/             # LLM provider handlers
│   ├── openai_handler.py
│   ├── anthropic_handler.py
│   ├── google_handler.py
│   ├── groq_handler.py
│   └── huggingface_handler.py
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security Notes

- Never commit your `.env` file with real API keys
- The `.env` file is excluded from git via `.gitignore`
- Use `.env.example` as a template for new setups
- Keep your API keys secure and rotate them regularly

## License

This project is open source and available under the [MIT License](LICENSE).

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Ensure you've activated the virtual environment and installed dependencies
2. **API key errors**: Verify your API keys are correctly set in the `.env` file
3. **CORS errors**: Make sure both servers are running on the specified ports
4. **Model not responding**: Check if you have sufficient API credits/quota

### Support

If you encounter issues:
1. Check the browser console for error messages
2. Verify your API keys are valid and have sufficient quota
3. Ensure all dependencies are installed correctly
4. Check that both frontend and backend servers are running

## Acknowledgments

- Built with vanilla HTML, CSS, and JavaScript for the frontend
- Python Flask for the backend API
- Supports multiple LLM providers for maximum flexibility