# SCANA-AI: Smart Contract Analysis & Network Automation

SCANA-AI is a powerful tool for analyzing food service contracts and monitoring delivery performance in real-time. It combines AI-powered contract analysis with advanced monitoring capabilities to ensure food safety and delivery compliance.

## Features

- 📄 **Contract Analysis**
  - Automated SLA clause extraction using GPT
  - Food safety requirement identification
  - Compliance validation
  - Breach detection

- 📊 **Performance Monitoring**
  - Real-time delivery tracking
  - Temperature monitoring
  - Quality assurance
  - Violation detection

- 🎯 **Risk Assessment**
  - Vendor risk profiling
  - Performance trend analysis
  - Fraud detection
  - Automated recommendations

## Project Structure

```
SCANA-AI/
├── src/                    # Source code
│   ├── api/               # API endpoints
│   │   ├── __init__.py
│   │   └── routes.py     # FastAPI routes
│   ├── core/             # Core business logic
│   │   ├── document/     # Document processing
│   │   ├── services/     # Business services
│   │   └── persistence/  # Data storage
│   └── ui/               # Streamlit UI
│       └── app.py        # Dashboard
├── data/                 # Sample data
│   ├── demo_vendor1.pdf  # Sample contract
│   └── demo_delivery.csv # Sample deliveries
├── tests/               # Test files
├── requirements.txt     # Dependencies
├── run.py              # Main application runner
└── README.md           # Documentation
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SCANA-AI.git
   cd SCANA-AI
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Create .env file with:
   OPENAI_API_KEY=your_api_key_here  # Optional, mock data used if not provided
   ```

## Running the Application

1. Start the application:
   ```bash
   python run.py
   ```
   This will:
   - Start the FastAPI server (automatically finds an available port)
   - Launch the Streamlit dashboard
   - Create necessary directories and files

2. Access the application:
   - API documentation: http://127.0.0.1:8088/docs (port may vary)
   - Dashboard: http://127.0.0.1:8501 (port may vary)

## Usage

1. Upload Contract:
   - Go to the dashboard
   - Upload a vendor contract PDF
   - View extracted SLA terms

2. Monitor Deliveries:
   - Upload delivery data CSV
   - View real-time monitoring
   - Check for violations

3. Analyze Performance:
   - View vendor risk profiles
   - Check compliance rates
   - Get improvement recommendations

## API Endpoints

- `GET /`: API status
- `GET /deliveries`: Get latest delivery data
- `GET /deliveries/batch`: Get multiple deliveries
- `POST /deliveries`: Create new delivery record

## Data Formats

### Delivery Log CSV Format
```csv
vendor_name,delivery_date,delivery_time,delivery_temperature,product_quality_score
Fresh Foods Inc.,2024-03-28,08:30,4.5,95
```

Required columns:
- `vendor_name`: String
- `delivery_date`: YYYY-MM-DD
- `delivery_time`: HH:MM
- `delivery_temperature`: Float (-30 to 30)
- `product_quality_score`: Float (0 to 100)

## Development

1. Run tests:
   ```bash
   python -m pytest tests/
   ```

2. Run API server only:
   ```bash
   uvicorn src.api.routes:app --reload
   ```

3. Run Streamlit only:
   ```bash
   streamlit run src/ui/app.py
   ```

## Troubleshooting

1. Port Conflicts:
   - The application automatically finds available ports
   - Default ports are 8088 (API) and 8501 (Streamlit)
   - If these ports are in use, the app will find alternatives

2. Data Storage:
   - Delivery data is stored in a temporary directory
   - If primary storage fails, data is saved to the current directory
   - Check console output for actual file locations

3. Common Issues:
   - If the API server fails to start, check if another instance is running
   - If data isn't showing up, verify the data file exists and has correct permissions
   - For GPT analysis issues, verify your OpenAI API key is set correctly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support:
- Open an issue in the GitHub repository
- Contact the maintainers
- Check the documentation 