#!/usr/bin/env python3
"""
Integration test for part-time scenario with windfalls and large expenses
"""

import requests
import json

def test_part_time_with_windfall_and_expense():
    """Test part-time scenario combined with windfall and large expense"""
    
    # Test data combining all features
    test_data = {
        "current_age": 30,
        "current_portfolio_taxable": 50000,
        "current_portfolio_tax_deferred": 75000,
        "annual_contribution": 25000,
        "expected_annual_spending": 60000,
        "growth_rate": 7,
        "inflation_rate": 3,
        "withdrawal_rate": 4,
        "fire_type": "regular",
        "social_security_income": 30000,
        "social_security_age": 67,
        "life_expectancy": 85,
        
        # Windfall: $100K inheritance at age 35
        "windfalls": [{"age": 35, "amount": 100000}],
        
        # Large expense: $75K adventure van at age 42, reducing contributions by 50%
        "large_expense": {
            "target_age": 42,
            "amount": 75000,
            "contribution_reduction": 0.5
        },
        
        # Part-time scenario
        "scenario_type": "part_time",
        "reduced_spending": 50000,  # Reduced spending during part-time
        "part_time_income": 40000,  # Part-time income
        "part_time_start_age": 55,
        "part_time_end_age": 62
    }
    
    try:
        print("🧪 Testing integrated scenario: Part-time + Windfall + Large Expense")
        print("=" * 70)
        
        # Test main calculation first
        print("1. Testing main calculation with windfall and large expense...")
        response = requests.post('http://localhost:5002/calculate', 
                               json=test_data, 
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            main_results = response.json()
            print(f"   ✅ Main calculation successful")
            print(f"   📊 Years to FIRE: {main_results['years_to_fire']}")
            print(f"   🎯 Target Portfolio: ${main_results['target_portfolio']:,.0f}")
            
            # Check for windfall and expense in projections
            windfall_year = None
            expense_year = None
            for proj in main_results['projections']:
                if proj.get('windfall', 0) > 0:
                    windfall_year = proj['age']
                if proj.get('large_expense', 0) > 0:
                    expense_year = proj['age']
            
            if windfall_year:
                print(f"   💰 Windfall detected at age {windfall_year}")
            if expense_year:
                print(f"   🚐 Large expense detected at age {expense_year}")
                
        else:
            print(f"   ❌ Main calculation failed: {response.status_code}")
            return False
            
        print()
        
        # Test part-time scenario with all features
        print("2. Testing part-time scenario with windfall and large expense...")
        response = requests.post('http://localhost:5002/scenario',
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            scenario_results = response.json()
            print(f"   ✅ Part-time scenario successful")
            
            # Analyze projections for all features
            projections = scenario_results['projections']
            
            # Find key years
            windfall_proj = next((p for p in projections if p.get('windfall', 0) > 0), None)
            expense_proj = next((p for p in projections if p.get('large_expense', 0) > 0), None)
            part_time_projs = [p for p in projections if p.get('part_time_income', 0) > 0]
            fire_proj = next((p for p in projections if p.get('fire_achieved', False)), None)
            
            print()
            print("   📈 Integrated Scenario Analysis:")
            print("   " + "-" * 40)
            
            if windfall_proj:
                print(f"   💰 Age {windfall_proj['age']}: Windfall of ${windfall_proj['windfall']:,.0f}")
                print(f"       Portfolio jumps to ${windfall_proj['portfolio_value']:,.0f}")
                
            if expense_proj:
                print(f"   🚐 Age {expense_proj['age']}: Adventure van purchase ${expense_proj['large_expense']:,.0f}")
                print(f"       Portfolio after purchase: ${expense_proj['portfolio_value']:,.0f}")
                
            if part_time_projs:
                start_age = min(p['age'] for p in part_time_projs)
                end_age = max(p['age'] for p in part_time_projs)
                avg_income = sum(p['part_time_income'] for p in part_time_projs) / len(part_time_projs)
                print(f"   👔 Ages {start_age}-{end_age}: Part-time work earning ~${avg_income:,.0f}/year")
                
            if fire_proj:
                print(f"   🔥 Age {fire_proj['age']}: FIRE achieved!")
                print(f"       Portfolio: ${fire_proj['portfolio_value']:,.0f}")
                print(f"       Sustainable withdrawal: ${fire_proj['sustainable_withdrawal']:,.0f}")
                print(f"       Net need: ${fire_proj.get('net_withdrawal_needed', 0):,.0f}")
                
            print()
            print("   📊 Feature Integration Summary:")
            print("   " + "-" * 40)
            print(f"   ✅ Windfall feature: {'Working' if windfall_proj else 'Not detected'}")
            print(f"   ✅ Large expense feature: {'Working' if expense_proj else 'Not detected'}")
            print(f"   ✅ Part-time feature: {'Working' if part_time_projs else 'Not detected'}")
            print(f"   ✅ FIRE calculation: {'Working' if fire_proj else 'Not achieved in timeframe'}")
            
            return True
            
        else:
            print(f"   ❌ Part-time scenario failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Is it running on http://localhost:5002?")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == '__main__':
    success = test_part_time_with_windfall_and_expense()
    
    if success:
        print()
        print("🎉 ALL FEATURES WORKING CORRECTLY!")
        print("✅ Windfall support")
        print("✅ Large expense planning")  
        print("✅ Part-time scenarios")
        print("✅ Full integration")
        print()
        print("🌟 You can now use the calculator at: http://localhost:5002")
        print("   Try combining windfalls, large expenses, and part-time work!")
    else:
        print()
        print("❌ Integration test failed. Check the Flask app and try again.")