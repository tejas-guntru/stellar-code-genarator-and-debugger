# Stellar CodeGen AI

An intelligent web application that transforms natural language descriptions into executable code using Google's Gemini AI.

![Stellar CodeGen AI](https://img.shields.io/badge/React-18.2.0-blue) ![Flask](https://img.shields.io/badge/Flask-2.3.3-green) ![Docker](https://img.shields.io/badge/Docker-Enabled-blue) ![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **AI-Powered Code Generation**: Convert natural language prompts to executable code
- **Multi-Language Support**: Python, HTML/CSS/JS, C++, Java
- **Secure Execution**: Docker container isolation for code execution
- **File Upload & Analysis**: Process and visualize data files
- **Live Preview**: Real-time output display
- **Interactive Interface**: Chat-style communication with status updates

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/stellar-codegen-ai.git
   cd stellar-codegen-ai
   ```

2. **Set up environment variables**
   ```bash
   # Create backend/.env file
   echo "GOOGLE_API_KEY=your_google_gemini_api_key_here" > backend/.env
   echo "FLASK_ENV=development" >> backend/.env
   ```

3. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   Open http://localhost:3000 in your browser

## 🛠️ Manual Setup

### Backend (Flask)

1. Navigate to backend directory
   ```bash
   cd backend
   ```

2. Create virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set environment variable
   ```bash
   export GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

4. Run the Flask server
   ```bash
   python app.py
   ```

### Frontend (React)

1. Navigate to frontend directory
   ```bash
   cd frontend
   ```

2. Install dependencies
   ```bash
   npm install
   ```

3. Start development server
   ```bash
   npm run dev
   ```

## 📁 Project Structure

```
stellar-codegen-ai/
├── backend/                 # Flask application
│   ├── app.py              # Main application file
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment variables
│   └── uploads/           # File upload directory
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   └── styles/        # CSS files
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
├── sandboxes/             # Docker sandbox configurations
│   ├── Dockerfile.python  # Python execution environment
│   ├── Dockerfile.cpp     # C++ execution environment
│   └── Dockerfile.java    # Java execution environment
└── docker-compose.yml     # Multi-container setup
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```
GOOGLE_API_KEY=your_google_gemini_api_key
FLASK_ENV=development
```

**Frontend (.env)**
```
VITE_API_URL=http://localhost:5000
```

### Obtaining Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create an API key in the API section
4. Add it to your backend/.env file

## 🐳 Docker Setup

### Build Sandbox Images

```bash
# Build Python sandbox
docker build -t stellar-python-sandbox:3.12 -f sandboxes/Dockerfile.python .

# Build C++ sandbox
docker build -t stellar-cpp-sandbox:latest -f sandboxes/Dockerfile.cpp .

# Build Java sandbox
docker build -t stellar-java-sandbox:latest -f sandboxes/Dockerfile.java .
```

### Start Sandbox Containers

```bash
docker run -d --name python-sandbox stellar-python-sandbox:3.12
docker run -d --name cpp-sandbox stellar-cpp-sandbox:latest
docker run -d --name java-sandbox stellar-java-sandbox:latest
```

## 💡 Usage

1. **Enter a prompt** describing the code you want to generate
2. **Select a programming language** from the dropdown
3. **Optionally upload a file** for data analysis
4. **Click Generate** and watch as your code is created and executed
5. **View the results** in the output panel and copy or download the code

### Example Prompts

- "Create a Python function to calculate Fibonacci sequence"
- "Generate a bar chart from CSV data showing sales by month"
- "Make a responsive login form with HTML and CSS"
- "Write a C++ program to sort an array using quicksort"

## 🛡️ Security Features

- Code execution in isolated Docker containers
- Timeout limits on execution
- Resource constraints on sandbox environments
- Input validation and sanitization

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check that Docker is running
2. Verify your Google API key is valid
3. Ensure all required ports (3000, 5000) are available
4. Check the browser console and Flask server logs for errors

For additional support, please open an issue on GitHub.

## 🙏 Acknowledgments

- Google Gemini AI for code generation capabilities
- React and Flask communities for excellent frameworks
- Docker for containerization technology

---

**Transform your ideas into code with Stellar CodeGen AI!**
