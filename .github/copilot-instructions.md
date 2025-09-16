# AI Event Manager - Copilot Instructions

## Project Overview & Vision
This is an AI-powered crowd control and event simulation system designed for the Great Malaysia AI Hackathon 2025. The system helps predict, simulate, and manage crowd movements at various events without requiring additional sensors or hardware. 

## Project Vision
Our vision is to create a decision-support tool that is not just predictive, but also explainable, interactive, and cost-aware. We aim to build a memorable demo that showcases a deep understanding of both the technical implementation and the real-world business value.

## Guiding Principles & The X-Factor
To win, we must do more than just meet the requirements. Our implementation will be guided by these principles:
- **Speed & Simplicity**: We use tools like Streamlit and uv to iterate at maximum velocity.
- **Professionalism & Quality**: We use ruff, pytest, and GitHub Actions to ensure our code is clean, tested, and reliable.
- **The Demo is the Product**: Every feature must contribute to a compelling, understandable, and impressive 3-minute demo.

Our project will stand out from others through these three X-Factors:
- **Explainable AI (XAI)**: Our AI won't just give recommendations; it will provide the "why", citing simulation data to build trust and provide deeper insights.
- **Cost-Aware AI**: The AI can optimize for either "Maximum Safety" or a "Balanced Safety & Cost" scenario, demonstrating a crucial understanding of real-world business constraints.
- **Interactive "What-If" Scenarios**: The demo will be a playable tool, not a static video. Users can tweak the AI's suggestions and see the impact in real-time.

## Architecture & Tech Stack

### Core Components
- **Frontend** (`src/app.py`): An interactive, multi-page dashboard built with **Streamlit** for event organizers.
- **Simulation Engine** (`src/simulation/`): A custom agent-based model built with **NumPy**. Handles crowd movement modeling based on venue layouts and event parameters.
- **Visualization** (`src/visualization/`): Creates dashboards and visual outputs via **Matplotlib** to render simulation results and recommendations.
- **AWS Integration** (`src/aws/bedrock.py`): The "brains" that provide recommendations and infrastructure for potential cloud deployment and scalability, powered by **Amazon Bedrock (CLAUDE)**.

### Core Development Tools
- **Package & Env Management**: **uv** (using pyproject.toml).
- **Code Quality**: **Ruff** for lightning-fast linting and formatting.
- **Testing Framework**: **Pytest** for targeted unit tests.
- **Automated CI**: **GitHub Actions** for automated code quality checks on every push.
- **Development Sandbox**: **Jupyter Notebooks** for rapid experimentation with simulation logic and AI prompts.

### Python Package Management with uv
Use uv exclusively for Python package management in this project.

#### Package Management Commands
- All Python dependencies **must be installed, synchronized, and locked** using uv
- Never use pip, pip-tools, poetry, or conda directly for dependency management

Use these commands:
- Install dependencies: `uv add <package>`
- Remove dependencies: `uv remove <package>`
- Sync dependencies: `uv sync`

#### Running Python Code
- Activate the virtual environment with `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows)
- Run a Python script with `uv run <script-name>.py`
- Run Python tools like Pytest with `uv run pytest` or `uv run ruff`
- Launch a Python repl with `uv run python`

#### Managing Scripts with PEP 723 Inline Metadata
- Run a Python script with inline metadata (dependencies defined at the top of the file) with: `uv run script.py`
- You can add or remove dependencies manually from the `dependencies =` section at the top of the script, or
- Or using uv CLI:
  - `uv add package-name --script script.py`
  - `uv remove package-name --script script.py`
- Sync the script dependencies with `uv sync --script script.py`

### Data Flow
1. Event data loaded from JSON configs (`data/event_config.json`)
2. Simulation models process venue layouts (`data/venue_map.csv`) 
3. Scenarios are run with different parameters
4. Results visualized for decision-making

## Development Workflow
This workflow is designed for speed and consistency. All commands must be run from the project's root directory.

### Environment Setup
```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync && uv lock
```

### Running the Application
```bash
# Run the main application
uv run python main.py

# Run the Streamlit web interface
uv run streamlit run src/app.py
```

### Testing
```bash
# Run tests
uv run pytest tests/
```

### Sandbox Workflow
1. **Experiment**: Develop new, complex logic (e.g., a new movement algorithm, a new AI prompt) inside a Jupyter Notebook in the /notebooks directory.
2. **Refactor**: Once the logic is proven, refactor it into clean, reusable functions.
3. **Integrate**: Move the final functions into the appropriate module in /src/.
4. **Test**: Write pytest tests for these new functions in the /tests/ directory.

## Project-Specific Conventions

### Project-Specific Configuration
1. **Configuration**
- Event configurations are stored in JSON format (`data/event_config.json`)
- Venue layouts are defined in CSV format (`data/venue_map.csv`)
- Simulation parameters are defined in the JSON configuration files
- All simulation parameters (attendee count, venue layout) MUST be loaded from the `/data` directory. Do not hardcode them in the application logic.
2. **Code Style**: Code style is non-negotiable and is automatically enforced by Ruff on save (if the VS Code extension is configured).
3. **Secrets**: Never commit AWS keys or other secrets to Git. Use environment variables for configuration.
4. **Commits**: Write clear, concise commit messages (e.g., "feat: Implement cost-aware AI prompt").

### Implementation Priorities
1. Focus on three key scenarios: entry rush, mid-event congestion, and evacuation
2. Emphasize simulation accuracy before visualization polish
3. Keep recommendations actionable for non-technical event staff

## Integration Points
- Streamlit for front-end visualization
- Potential AWS services for deployment (boto3 dependency)
- Support for ingesting ticketing, scheduling, and venue data

## When Adding New Features
- Add appropriate simulation parameters in `data/event_config.json`
- Update visualization components to display new metrics
- Document scenario coverage in docstrings
- Consider both small (1,000) and large (50,000+) event scales

## Submission Checklist
This is our roadmap to a complete and winning submission, directly addressing the judging criteria.
- [ ] **Recorded Demo Video (pitch/demo_video.mp4)**: A crisp, sub-3-minute video showcasing the user experience and the three X-Factors.
- [ ] **Pitch Deck (pitch/pitch.pptx)**: Emphasizes Novelty, Impact, Cost, and Architecture.
- [ ] **Architecture Diagram (pitch/architecture.png)**: A clear, professional diagram of our system.
- [ ] **AWS Screenshots (pitch/aws_screenshots/)**: Visual proof of our configured AI services.
- [ ] **Code Zip File (ai-event-manager.zip)**: A zipped archive of the entire project repository.