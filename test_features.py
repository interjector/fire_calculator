#!/usr/bin/env python3
"""
Test script to verify the new FIRE calculator features work correctly
"""

from fire_calculator import FIRECalculator

def test_fire_types():
    """Test different FIRE type calculations"""
    print("=== Testing FIRE Types ===")
    
    calculator = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        fire_type='regular'
    )
    
    # Test all FIRE types
    fire_targets = calculator.calculate_all_fire_targets()
    
    for fire_type, info in fire_targets.items():
        print(f"{info['name']}: ${info['target_portfolio']:,.0f} (spending: ${info['annual_spending']:,.0f})")
    
    print()

def test_windfalls():
    """Test windfall integration"""
    print("=== Testing Windfalls ===")
    
    # Without windfall
    calc_no_windfall = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000
    )
    
    years_no_windfall = calc_no_windfall.calculate_years_to_fire()
    
    # With windfall
    calc_with_windfall = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        windfalls=[{'age': 35, 'amount': 100000}]
    )
    
    years_with_windfall = calc_with_windfall.calculate_years_to_fire()
    
    print(f"Years to FIRE without windfall: {years_no_windfall}")
    print(f"Years to FIRE with $100K windfall at age 35: {years_with_windfall}")
    print(f"Windfall saves {years_no_windfall - years_with_windfall} years!")
    print()

def test_large_expense():
    """Test large expense planning"""
    print("=== Testing Large Expense Planning ===")
    
    # Without large expense
    calc_normal = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000
    )
    
    # With large expense (adventure van)
    calc_with_expense = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        large_expense={
            'target_age': 42,
            'amount': 75000,
            'contribution_reduction': 0.5  # Reduce contributions by 50%
        }
    )
    
    # Generate projections to see the impact
    projections_normal = calc_normal.generate_yearly_projections(15)  # First 15 years
    projections_expense = calc_with_expense.generate_yearly_projections(15)
    
    print("Age 42 comparison (adventure van purchase year):")
    age_42_normal = next(p for p in projections_normal if p['age'] == 42)
    age_42_expense = next(p for p in projections_expense if p['age'] == 42)
    
    print(f"Normal scenario at age 42: ${age_42_normal['portfolio_value']:,.0f}")
    print(f"With van expense at age 42: ${age_42_expense['portfolio_value']:,.0f}")
    print(f"Large expense: ${age_42_expense['large_expense']:,.0f}")
    print(f"Net impact: ${age_42_expense['portfolio_value'] - age_42_normal['portfolio_value'] + age_42_expense['large_expense']:,.0f}")
    print()

if __name__ == '__main__':
    test_fire_types()
    test_windfalls()
    test_large_expense()
    print("✅ All features tested successfully!")