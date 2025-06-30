from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
from fire_calculator import FIRECalculator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        
        # Extract input parameters
        current_age = int(data['current_age'])
        current_portfolio_taxable = float(data['current_portfolio_taxable'])
        current_portfolio_tax_deferred = float(data['current_portfolio_tax_deferred'])
        annual_contribution = float(data['annual_contribution'])
        expected_annual_spending = float(data['expected_annual_spending'])
        growth_rate = float(data['growth_rate']) / 100  # Convert percentage to decimal
        inflation_rate = float(data['inflation_rate']) / 100  # Convert percentage to decimal
        withdrawal_rate = float(data.get('withdrawal_rate', 4.0)) / 100  # Default 4% rule
        social_security_income = float(data.get('social_security_income', 0))
        social_security_age = int(data.get('social_security_age', 67))
        desired_retirement_age = int(data['desired_retirement_age']) if data.get('desired_retirement_age') else None
        life_expectancy = int(data.get('life_expectancy', 85))
        fire_type = data.get('fire_type', 'regular')
        
        # Parse windfalls
        windfalls = []
        if data.get('windfalls'):
            for windfall in data['windfalls']:
                windfalls.append({
                    'age': int(windfall['age']),
                    'amount': float(windfall['amount'])
                })
        
        # Parse large expense
        large_expense = {}
        if data.get('large_expense'):
            large_expense = {
                'target_age': int(data['large_expense']['target_age']),
                'amount': float(data['large_expense']['amount']),
                'contribution_reduction': float(data['large_expense'].get('contribution_reduction', 0))
            }
        
        # Create calculator instance
        calculator = FIRECalculator(
            current_age=current_age,
            current_portfolio_taxable=current_portfolio_taxable,
            current_portfolio_tax_deferred=current_portfolio_tax_deferred,
            annual_contribution=annual_contribution,
            expected_annual_spending=expected_annual_spending,
            growth_rate=growth_rate,
            inflation_rate=inflation_rate,
            withdrawal_rate=withdrawal_rate,
            social_security_income=social_security_income,
            social_security_age=social_security_age,
            desired_retirement_age=desired_retirement_age,
            life_expectancy=life_expectancy,
            fire_type=fire_type,
            windfalls=windfalls,
            large_expense=large_expense
        )
        
        # Calculate target portfolio value
        target_portfolio = calculator.calculate_target_portfolio()
        
        # Calculate years to FIRE
        years_to_fire = calculator.calculate_years_to_fire()
        
        # Generate yearly projections (to life expectancy)
        projections = calculator.generate_yearly_projections()
        
        # Calculate scenarios
        scenarios = calculator.calculate_scenarios()
        
        # Check retirement readiness
        retirement_readiness = calculator.check_retirement_readiness()
        
        # Calculate all FIRE targets
        fire_targets = calculator.calculate_all_fire_targets()
        
        response = {
            'target_portfolio': target_portfolio,
            'years_to_fire': years_to_fire,
            'fire_age': current_age + years_to_fire,
            'projections': projections,
            'scenarios': scenarios,
            'retirement_readiness': retirement_readiness,
            'fire_targets': fire_targets,
            'current_fire_type': fire_type
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/scenario', methods=['POST'])
def scenario_analysis():
    try:
        data = request.get_json()
        
        # Extract scenario parameters
        current_age = int(data['current_age'])
        current_portfolio_taxable = float(data['current_portfolio_taxable'])
        current_portfolio_tax_deferred = float(data['current_portfolio_tax_deferred'])
        annual_contribution = float(data.get('annual_contribution', 0))  # Get from form data
        expected_annual_spending = float(data['expected_annual_spending'])
        scenario_type = data['scenario_type']
        
        # Extract additional parameters
        social_security_income = float(data.get('social_security_income', 0))
        social_security_age = int(data.get('social_security_age', 67))
        life_expectancy = int(data.get('life_expectancy', 85))
        growth_rate = float(data.get('growth_rate', 7)) / 100
        inflation_rate = float(data.get('inflation_rate', 3)) / 100
        withdrawal_rate = float(data.get('withdrawal_rate', 4)) / 100
        desired_retirement_age = int(data['desired_retirement_age']) if data.get('desired_retirement_age') else None
        fire_type = data.get('fire_type', 'regular')
        
        # Parse windfalls for scenarios
        windfalls = []
        if data.get('windfalls'):
            for windfall in data['windfalls']:
                windfalls.append({
                    'age': int(windfall['age']),
                    'amount': float(windfall['amount'])
                })
        
        # Parse large expense for scenarios
        large_expense = {}
        if data.get('large_expense'):
            large_expense = {
                'target_age': int(data['large_expense']['target_age']),
                'amount': float(data['large_expense']['amount']),
                'contribution_reduction': float(data['large_expense'].get('contribution_reduction', 0))
            }
        
        # Set annual contribution based on scenario type
        scenario_annual_contribution = 0 if scenario_type == 'no_contributions' else annual_contribution
        
        calculator = FIRECalculator(
            current_age=current_age,
            current_portfolio_taxable=current_portfolio_taxable,
            current_portfolio_tax_deferred=current_portfolio_tax_deferred,
            annual_contribution=scenario_annual_contribution,
            expected_annual_spending=expected_annual_spending,
            growth_rate=growth_rate,
            inflation_rate=inflation_rate,
            withdrawal_rate=withdrawal_rate,
            social_security_income=social_security_income,
            social_security_age=social_security_age,
            desired_retirement_age=desired_retirement_age,
            life_expectancy=life_expectancy,
            fire_type=fire_type,
            windfalls=windfalls,
            large_expense=large_expense
        )
        
        if scenario_type == 'no_contributions':
            # Portfolio appreciation without additional contributions
            projections = calculator.generate_no_contribution_projections(life_expectancy - current_age)
        elif scenario_type == 'part_time':
            # Reduced spending with part-time work for specified period
            reduced_spending = float(data['reduced_spending'])
            part_time_income = float(data['part_time_income'])
            part_time_start_age = int(data.get('part_time_start_age', 55))
            part_time_end_age = int(data.get('part_time_end_age', 62))
            projections = calculator.generate_part_time_projections(
                reduced_spending, part_time_income, part_time_start_age, part_time_end_age, life_expectancy - current_age
            )
        
        return jsonify({'projections': projections})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/monte_carlo', methods=['POST'])
def monte_carlo_simulation():
    try:
        data = request.get_json()
        
        # Extract parameters for Monte Carlo
        current_age = int(data['current_age'])
        current_portfolio_taxable = float(data['current_portfolio_taxable'])
        current_portfolio_tax_deferred = float(data['current_portfolio_tax_deferred'])
        annual_contribution = float(data['annual_contribution'])
        expected_annual_spending = float(data['expected_annual_spending'])
        growth_rate = float(data['growth_rate']) / 100
        inflation_rate = float(data['inflation_rate']) / 100
        withdrawal_rate = float(data.get('withdrawal_rate', 4.0)) / 100
        social_security_income = float(data.get('social_security_income', 0))
        social_security_age = int(data.get('social_security_age', 67))
        life_expectancy = int(data.get('life_expectancy', 85))
        
        num_simulations = int(data.get('num_simulations', 1000))
        years = int(data.get('years', min(30, life_expectancy - current_age)))
        
        calculator = FIRECalculator(
            current_age=current_age,
            current_portfolio_taxable=current_portfolio_taxable,
            current_portfolio_tax_deferred=current_portfolio_tax_deferred,
            annual_contribution=annual_contribution,
            expected_annual_spending=expected_annual_spending,
            growth_rate=growth_rate,
            inflation_rate=inflation_rate,
            withdrawal_rate=withdrawal_rate,
            social_security_income=social_security_income,
            social_security_age=social_security_age,
            life_expectancy=life_expectancy
        )
        
        monte_carlo_results = calculator.run_monte_carlo_simulation(num_simulations, years)
        
        return jsonify(monte_carlo_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)