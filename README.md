# FIRE Calculator

A Python-based web application to calculate and model your path to Financial Independence, Retire Early (FIRE).

## Features
the fir
- Calculate target portfolio value based on expected retirement spending
- Project portfolio growth year over year with customizable growth and inflation rates
- Determine when you'll achieve FIRE based on current savings and contributions
- Interactive charts showing portfolio projections
- Scenario analysis including:
  - Conservative vs optimistic market conditions
  - Higher contribution scenarios
  - No additional contributions scenario
  - Part-time work with reduced spending scenario
- Support for both taxable and tax-deferred accounts

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Enter your financial information:
   - Current age
   - Current portfolio values (taxable and tax-deferred)
   - Annual contribution amount
   - Expected annual spending in retirement
   - Expected growth rate (default: 7%)
   - Expected inflation rate (default: 3%)
   - Safe withdrawal rate (default: 4%)

4. Click "Calculate FIRE Plan" to see your results

## Key Concepts

### The 4% Rule
The application uses the 4% rule by default, which suggests you can safely withdraw 4% of your portfolio annually in retirement. Your target portfolio is calculated as: Annual Spending ÷ Withdrawal Rate

### Portfolio Projections
The calculator shows year-by-year projections including:
- Portfolio value growth
- Target portfolio milestone
- Sustainable withdrawal amount (portfolio × withdrawal rate)
- Inflation-adjusted spending needs

### Scenario Analysis
Compare different scenarios to understand how changes in contributions, market conditions, or retirement strategy affect your FIRE timeline.

## File Structure

```
fire_calculator/
├── app.py                 # Flask web application
├── fire_calculator.py     # Core calculation logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
└── static/
    └── calculator.js     # Frontend JavaScript
```

## Customization

You can modify the default assumptions by editing the values in `fire_calculator.py` or by adjusting the form inputs in the web interface.

## Disclaimer

This calculator is for educational and planning purposes only. Actual investment returns, inflation, and life circumstances will vary. Please consult with a financial advisor for personalized advice.
