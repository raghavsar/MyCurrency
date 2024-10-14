# Currency Codes Project

This project provides a list of currency codes and their descriptions. It includes a Python script to retrieve and display currency codes, with support for environment variables for configuration. Additionally, a Postman collection is provided for easy API testing.


In settings.py I have used Adapter design thorough which you can enable or disable the Providers.

## Prerequisites

Before you begin, ensure you have Python installed on your machine. You can download it from [here](https://www.python.org/downloads/). To verify Python is installed, run:

```bash
python --version

git clone https://github.com/boxabhi/MyCurrency.git
cd mycurrency


python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     


pip install -r requirements.txt

cp .sampleenv .env

CURRENCY_BEACON_API_KEY=your_api_key_here


- **Postman Collection**: Added a section that explains how to import the provided Postman collection for testing the APIs.