# 🔍 Zurvey

**AI-powered survey response validation for market research excellence**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 📊 The Problem

Open-ended survey responses are critical for market insights but frequently compromised by:
- Gibberish text
- Copy-pasted responses
- Off-topic answers
- AI-generated content

Manual review processes are labor-intensive, error-prone, and delay valuable insights.

## 💡 Our Solution

Zurvey leverages advanced AI to automatically validate open-ended survey responses, ensuring data integrity while dramatically reducing manual effort.

### Key Benefits

- **Automated Quality Control**: Eliminate gibberish, duplicates, and off-topic responses
- **AI Detection**: Identify machine-generated content
- **Time Efficiency**: Reduce validation time by up to 90%
- **Enhanced Data Integrity**: Make decisions based on authentic human feedback
- **Actionable Insights**: Generate reliable market intelligence faster

## 🧠 Multi-Agent Architecture

Zurvey employs a sophisticated multi-agent system to thoroughly analyze survey responses:

1. **Preprocessing Agent**: Handles initial cleaning and normalization
2. **Quality Filter Agent**: Detects empty, short, or disturbing content (Score 0-1)
3. **Relevance Agent**: Evaluates response relevance to survey topics (Score 0-5)
4. **Complexity & Coherence Agent**: Analyzes linguistic structure and sophistication (Score 0-5)
5. **Sentiment & Toxicity Agent**: Evaluates emotional content and potentially harmful language (Score -2 to 2)
6. **AI Detection Agent**: Identifies signs of AI-generated responses (Score 0-3)
7. **Final Decision Agent**: Aggregates all agent scores into a comprehensive quality rating

Each specialized agent applies specific scoring criteria, providing a nuanced evaluation across multiple dimensions of quality. The system then produces a total score to flag responses as either high or low quality based on configurable thresholds.

![Zurvey Workflow](assets/12.png)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git

### Installation

1. Clone the repository
```bash
git clone https://github.com/team-recursion/zurvey.git
cd zurvey
```

2. Create and activate a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages
```bash
pip install -r requirements.txt
```

## 🔧 Usage

### 1. Configure File Paths

Edit the file paths in:
- `Codes/Pre-Processing.py`
- `Codes/Agent-Orchestration.py`

### 2. Run the Validation Pipeline

```bash
python Codes/Agent-Orchestration.py
```

### 3. Set Validation Thresholds

Configure your quality thresholds in:
```bash
python utils/thresholding.py
```

### 4. View Results and Analytics

Generate comparison reports and visualizations:
```bash
python utils/comparison.py
python utils/plots.py
```

## 📈 How It Works

1. **Pre-processing**: Clean and normalize survey response data
2. **Multi-agent Validation**: Specialized AI agents analyze different quality aspects
3. **Scoring**: Responses receive quality scores across multiple dimensions
4. **Thresholding**: Configurable quality thresholds filter responses
5. **Reporting**: Comprehensive analytics on validation results

## 🏆 Team Recursion

Zurvey is proudly developed by Team Recursion, a group of students passionate about improving survey data quality.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
