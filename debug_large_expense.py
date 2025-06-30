#!/usr/bin/env python3
"""
Debug script to identify large expense bugs that could cause massive negative values
"""

from fire_calculator import FIRECalculator

def test_extreme_large_expense():
    """Test with extreme large expense values"""
    print("=== Testing Extreme Large Expense Scenarios ===")
    
    # Test case 1: Large expense larger than portfolio
    print("\n1. Testing large expense larger than portfolio:")
    calc = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        large_expense={
            'target_age': 35,
            'amount': 1000000,  # $1M expense on $125K portfolio
            'contribution_reduction': 0.5
        }
    )
    
    projections = calc.generate_yearly_projections(20)
    
    # Check age 35 (expense year)
    age_35_proj = next(p for p in projections if p['age'] == 35)
    print(f"   Age 35 portfolio value: ${age_35_proj['portfolio_value']:,.2f}")
    print(f"   Large expense: ${age_35_proj['large_expense']:,.2f}")
    print(f"   Annual contribution: ${age_35_proj['annual_contribution']:,.2f}")
    
    # Check age 36 (after expense)
    age_36_proj = next(p for p in projections if p['age'] == 36)
    print(f"   Age 36 portfolio value: ${age_36_proj['portfolio_value']:,.2f}")
    
    # Test case 2: 100% contribution reduction
    print("\n2. Testing 100% contribution reduction:")
    calc = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        large_expense={
            'target_age': 35,
            'amount': 50000,
            'contribution_reduction': 1.0  # 100% reduction
        }
    )
    
    projections = calc.generate_yearly_projections(10)
    
    for age in [34, 35, 36]:
        proj = next(p for p in projections if p['age'] == age)
        print(f"   Age {age}: Portfolio ${proj['portfolio_value']:,.2f}, Contribution ${proj['annual_contribution']:,.2f}")
    
    # Test case 3: Contribution reduction > 1.0
    print("\n3. Testing contribution reduction > 1.0:")
    calc = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        large_expense={
            'target_age': 35,
            'amount': 50000,
            'contribution_reduction': 1.5  # 150% reduction - BUG POTENTIAL
        }
    )
    
    projections = calc.generate_yearly_projections(10)
    
    for age in [34, 35, 36]:
        proj = next(p for p in projections if p['age'] == age)
        print(f"   Age {age}: Portfolio ${proj['portfolio_value']:,.2f}, Contribution ${proj['annual_contribution']:,.2f}")
    
    # Test case 4: Negative contribution reduction
    print("\n4. Testing negative contribution reduction:")
    calc = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        large_expense={
            'target_age': 35,
            'amount': 50000,
            'contribution_reduction': -0.5  # Negative reduction - BUG POTENTIAL
        }
    )
    
    projections = calc.generate_yearly_projections(10)
    
    for age in [34, 35, 36]:
        proj = next(p for p in projections if p['age'] == age)
        print(f"   Age {age}: Portfolio ${proj['portfolio_value']:,.2f}, Contribution ${proj['annual_contribution']:,.2f}")

def test_multiple_large_expenses():
    """Test with multiple large expenses in the same year"""
    print("\n=== Testing Multiple Large Expenses ===")
    
    # Create two calculators with the same large expense to simulate double application
    calc = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        large_expense={
            'target_age': 35,
            'amount': 100000,
            'contribution_reduction': 0.5
        }
    )
    
    projections = calc.generate_yearly_projections(10)
    
    # Check for the target age
    age_35_proj = next(p for p in projections if p['age'] == 35)
    print(f"   Age 35: Portfolio ${age_35_proj['portfolio_value']:,.2f}, Large expense ${age_35_proj['large_expense']:,.2f}")

def test_contribution_reduction_edge_cases():
    """Test edge cases in contribution reduction logic"""
    print("\n=== Testing Contribution Reduction Edge Cases ===")
    
    # Test with target_age in the past
    print("\n1. Testing target_age in the past:")
    calc = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        large_expense={
            'target_age': 25,  # In the past
            'amount': 50000,
            'contribution_reduction': 0.5
        }
    )
    
    projections = calc.generate_yearly_projections(5)
    
    for age in [30, 31, 32]:
        proj = next(p for p in projections if p['age'] == age)
        print(f"   Age {age}: Contribution ${proj['annual_contribution']:,.2f}")
    
    # Test with very high target_age
    print("\n2. Testing very high target_age:")
    calc = FIRECalculator(
        current_age=30,
        current_portfolio_taxable=50000,
        current_portfolio_tax_deferred=75000,
        annual_contribution=25000,
        expected_annual_spending=60000,
        large_expense={
            'target_age': 100,  # Very high
            'amount': 50000,
            'contribution_reduction': 0.5
        }
    )
    
    projections = calc.generate_yearly_projections(5)
    
    for age in [30, 31, 32]:
        proj = next(p for p in projections if p['age'] == age)
        print(f"   Age {age}: Contribution ${proj['annual_contribution']:,.2f}")

if __name__ == '__main__':
    test_extreme_large_expense()
    test_multiple_large_expenses()
    test_contribution_reduction_edge_cases()
    print("\n=== Debug complete ===")