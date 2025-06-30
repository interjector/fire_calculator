import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fire_calculator import FIRECalculator
import numpy as np
import requests
import json
import time
from datetime import datetime

st.set_page_config(
    page_title="VIBE FIRE Calculator",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔥 VIBE FIRE Calculator")
st.markdown("Financial Independence, Retire Early Calculator")

# Sidebar for inputs
st.sidebar.header("Your Financial Profile")


# Basic Information
st.sidebar.subheader("Basic Information")
current_age = st.sidebar.number_input("Current Age", min_value=18, max_value=100, value=30)
current_portfolio_taxable = st.sidebar.number_input("Current Taxable Portfolio ($)", min_value=0, value=50000, step=1000)
current_portfolio_tax_deferred = st.sidebar.number_input("Current Tax-Deferred Portfolio ($)", min_value=0, value=25000, step=1000)
annual_contribution = st.sidebar.number_input("Annual Contribution ($)", min_value=0, value=20000, step=1000)
expected_annual_spending = st.sidebar.number_input("Expected Annual Spending in Retirement ($)", min_value=0, value=50000, step=1000)

# Advanced Settings
st.sidebar.subheader("Advanced Settings")
growth_rate = st.sidebar.slider("Expected Annual Growth Rate (%)", min_value=1.0, max_value=15.0, value=7.0, step=0.5) / 100
inflation_rate = st.sidebar.slider("Expected Inflation Rate (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.1) / 100
withdrawal_rate = st.sidebar.slider("Safe Withdrawal Rate (%)", min_value=2.0, max_value=8.0, value=4.0, step=0.1) / 100

# FIRE Type
fire_type = st.sidebar.selectbox("FIRE Type", ["lean", "regular", "fat"], index=1)

# Social Security
st.sidebar.subheader("Social Security")
social_security_income = st.sidebar.number_input("Expected Annual Social Security ($)", min_value=0, value=0, step=1000)
social_security_age = st.sidebar.number_input("Social Security Start Age", min_value=62, max_value=70, value=67)

# Optional Settings
st.sidebar.subheader("Optional Settings")
desired_retirement_age = st.sidebar.number_input("Desired Retirement Age (optional)", min_value=current_age, max_value=100, value=None)
life_expectancy = st.sidebar.number_input("Life Expectancy", min_value=current_age, max_value=120, value=85)

# Windfalls
st.sidebar.subheader("Expected Windfalls")
num_windfalls = st.sidebar.number_input("Number of Windfalls", min_value=0, max_value=10, value=0)
windfalls = []
for i in range(num_windfalls):
    st.sidebar.write(f"Windfall {i+1}")
    age = st.sidebar.number_input(f"Age for windfall {i+1}", min_value=current_age, max_value=100, value=current_age+5, key=f"windfall_age_{i}")
    amount = st.sidebar.number_input(f"Amount for windfall {i+1} ($)", min_value=0, value=10000, step=1000, key=f"windfall_amount_{i}")
    windfalls.append({"age": age, "amount": amount})

# Large Expense
st.sidebar.subheader("Large Expense")
has_large_expense = st.sidebar.checkbox("Include Large Expense")
large_expense = {}
if has_large_expense:
    expense_type = st.sidebar.radio("Expense Type", ["Single Year", "Multi-Year"])
    
    # Funding strategy selection
    st.sidebar.write("**Funding Strategy:**")
    funding_strategy = st.sidebar.radio(
        "How to fund this expense:",
        ["Reduce Contributions", "Portfolio Withdrawal", "Mixed Approach"],
        help="Choose how you want to pay for this expense"
    )
    
    if expense_type == "Single Year":
        large_expense = {
            "target_age": st.sidebar.number_input("Age for Large Expense", min_value=current_age, max_value=100, value=current_age+10),
            "amount": st.sidebar.number_input("Large Expense Amount ($)", min_value=0, value=50000, step=1000),
            "type": "single",
            "funding_strategy": funding_strategy.lower().replace(" ", "_")
        }
        
        # Add specific controls based on funding strategy
        if funding_strategy == "Mixed Approach":
            max_contribution_reduction = st.sidebar.number_input(
                "Max Annual Contribution Reduction ($)", 
                min_value=0, 
                max_value=annual_contribution, 
                value=min(large_expense["amount"], annual_contribution), 
                step=1000,
                help="Reduce contributions up to this amount, then take remainder from portfolio"
            )
            large_expense["max_contribution_reduction"] = max_contribution_reduction
        elif funding_strategy == "Reduce Contributions":
            st.sidebar.info(f"💡 This will reduce your annual contribution by ${large_expense['amount']:,} in the expense year")
            if large_expense["amount"] > annual_contribution:
                st.sidebar.warning(f"⚠️ Expense (${large_expense['amount']:,}) exceeds annual contribution (${annual_contribution:,}). Excess will be taken from portfolio.")
    else:
        large_expense = {
            "start_age": st.sidebar.number_input("Start Age for Multi-Year Expense", min_value=current_age, max_value=100, value=current_age+10),
            "end_age": st.sidebar.number_input("End Age for Multi-Year Expense", min_value=current_age, max_value=100, value=current_age+12),
            "annual_amount": st.sidebar.number_input("Annual Expense Amount ($)", min_value=0, value=30000, step=1000),
            "type": "multi",
            "funding_strategy": funding_strategy.lower().replace(" ", "_")
        }
        # Ensure end_age >= start_age
        if large_expense["end_age"] < large_expense["start_age"]:
            large_expense["end_age"] = large_expense["start_age"]
            
        # Add specific controls based on funding strategy
        if funding_strategy == "Mixed Approach":
            max_annual_contribution_reduction = st.sidebar.number_input(
                "Max Annual Contribution Reduction ($)", 
                min_value=0, 
                max_value=annual_contribution, 
                value=min(large_expense["annual_amount"], annual_contribution), 
                step=1000,
                help="Reduce contributions up to this amount per year, then take remainder from portfolio"
            )
            large_expense["max_annual_contribution_reduction"] = max_annual_contribution_reduction
        elif funding_strategy == "Reduce Contributions":
            st.sidebar.info(f"💡 This will reduce your annual contribution by ${large_expense['annual_amount']:,} each year")
            if large_expense["annual_amount"] > annual_contribution:
                st.sidebar.warning(f"⚠️ Annual expense (${large_expense['annual_amount']:,}) exceeds annual contribution (${annual_contribution:,}). Excess will be taken from portfolio.")

# Calculate button
if st.sidebar.button("Calculate FIRE Plan", type="primary"):
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
    
    # Store results in session state
    st.session_state.calculator = calculator
    st.session_state.target_portfolio = calculator.calculate_target_portfolio()
    st.session_state.years_to_fire = calculator.calculate_years_to_fire()
    if st.session_state.years_to_fire is not None:
        st.session_state.fire_age = current_age + st.session_state.years_to_fire
    else:
        st.session_state.fire_age = None
    st.session_state.projections = calculator.generate_yearly_projections()
    st.session_state.scenarios = calculator.calculate_scenarios()
    st.session_state.retirement_readiness = calculator.check_retirement_readiness()
    st.session_state.fire_targets = calculator.calculate_all_fire_targets()

# Display results if available
if 'calculator' in st.session_state:
    # Check if we should use scenario data for metrics calculation
    if 'current_scenario' in st.session_state:
        # Use scenario data to calculate updated metrics
        scenario_projections = st.session_state.current_scenario['data']
        scenario_df = pd.DataFrame(scenario_projections)
        
        # Find when FIRE is achieved in the scenario
        fire_achieved_rows = scenario_df[scenario_df['fire_achieved'] == True]
        if not fire_achieved_rows.empty:
            scenario_fire_age = fire_achieved_rows.iloc[0]['age']
            scenario_years_to_fire = scenario_fire_age - current_age
            scenario_target_portfolio = fire_achieved_rows.iloc[0]['target_portfolio']
        else:
            # FIRE not achieved in scenario
            scenario_fire_age = None
            scenario_years_to_fire = None
            scenario_target_portfolio = st.session_state.target_portfolio
            
        # Use scenario metrics
        display_fire_age = scenario_fire_age
        display_years_to_fire = scenario_years_to_fire
        display_target_portfolio = scenario_target_portfolio
        
        # Show which scenario is being displayed
        scenario_titles = {
            'no_contributions': "No Contributions Scenario",
            'part_time': "Part-Time Work Scenario", 
            'barista_fire': "Barista FIRE Scenario"
        }
        scenario_name = scenario_titles.get(st.session_state.current_scenario['type'], "Current Scenario")
        st.info(f"📊 **Showing metrics for: {scenario_name}**")
    else:
        # Use original plan metrics but recalculate if large expense or windfalls changed
        # Recalculate to account for large expenses and windfalls
        temp_calculator = FIRECalculator(
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
        
        updated_years_to_fire = temp_calculator.calculate_years_to_fire()
        updated_target_portfolio = temp_calculator.calculate_target_portfolio()
        
        if updated_years_to_fire is not None:
            display_fire_age = current_age + updated_years_to_fire
            display_years_to_fire = updated_years_to_fire
        else:
            display_fire_age = None
            display_years_to_fire = None
        display_target_portfolio = updated_target_portfolio
    
    # Retirement readiness alert
    if desired_retirement_age is not None and display_fire_age is not None:
        if display_fire_age <= desired_retirement_age:
            st.success(f"🎯 **On Track!** You're projected to achieve FIRE at age {display_fire_age:.0f}, which is {desired_retirement_age - display_fire_age:.1f} years before your target retirement age of {desired_retirement_age}.")
        else:
            years_behind = display_fire_age - desired_retirement_age
            st.error(f"⚠️ **Behind Target!** You're projected to achieve FIRE at age {display_fire_age:.0f}, which is {years_behind:.1f} years after your target retirement age of {desired_retirement_age}. Consider increasing contributions or adjusting your retirement timeline.")
    elif display_fire_age is not None:
        st.info(f"📊 You're projected to achieve FIRE at age {display_fire_age:.0f}. Set a desired retirement age in the sidebar to see if you're on track!")
    else:
        st.warning("⚠️ FIRE not achieved within the projected timeframe. Consider increasing contributions or reducing expenses.")
    
    # Main results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Target Portfolio", f"${display_target_portfolio:,.0f}")
    
    with col2:
        if display_years_to_fire is not None:
            st.metric("Years to FIRE", f"{display_years_to_fire:.1f}")
        else:
            st.metric("Years to FIRE", "Not Achieved")
    
    with col3:
        if display_fire_age is not None:
            st.metric("FIRE Age", f"{display_fire_age:.0f}")
        else:
            st.metric("FIRE Age", "Not Achieved")
    
    with col4:
        current_total = current_portfolio_taxable + current_portfolio_tax_deferred
        st.metric("Current Portfolio", f"${current_total:,.0f}")
    
    # FIRE Targets
    st.subheader("FIRE Targets by Type")
    fire_targets_df = pd.DataFrame([
        {"Type": "Lean FIRE", "Amount": f"${st.session_state.fire_targets['lean']['target_portfolio']:,.0f}"},
        {"Type": "Regular FIRE", "Amount": f"${st.session_state.fire_targets['regular']['target_portfolio']:,.0f}"},
        {"Type": "Fat FIRE", "Amount": f"${st.session_state.fire_targets['fat']['target_portfolio']:,.0f}"}
    ])
    st.table(fire_targets_df)
    
    # Portfolio Growth Chart
    st.subheader("Portfolio Growth Projection")
    
    projections_df = pd.DataFrame(st.session_state.projections)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=projections_df['age'],
        y=projections_df['portfolio_value'],
        mode='lines',
        name='Your Portfolio Growth',
        line=dict(color='blue', width=3),
        showlegend=True
    ))
    
    # Add all FIRE target lines with legend entries
    fire_colors = {
        'lean': '#28a745',    # Green
        'regular': '#dc3545', # Red  
        'fat': '#ffc107'      # Yellow/Gold
    }
    
    # Calculate years to reach each FIRE target
    fire_achievements = {}
    for target_type in ['lean', 'regular', 'fat']:
        if target_type in st.session_state.fire_targets:
            target_value = st.session_state.fire_targets[target_type]['target_portfolio']
            # Find first age where portfolio exceeds target
            achieved_rows = projections_df[projections_df['portfolio_value'] >= target_value]
            if not achieved_rows.empty:
                fire_age = achieved_rows.iloc[0]['age']
                years_to_fire = fire_age - current_age
                fire_achievements[target_type] = {
                    'age': fire_age,
                    'years': years_to_fire,
                    'target': target_value
                }
    
    for target_type, target_data in st.session_state.fire_targets.items():
        if target_type in ['lean', 'regular', 'fat']:  # Only show main FIRE types
            target_value = target_data['target_portfolio']
            
            # Bold the selected FIRE type
            line_width = 4 if target_type == fire_type else 2
            line_dash = "solid" if target_type == fire_type else "dash"
            
            # Create legend label with time to FIRE
            if target_type in fire_achievements:
                years_to_fire = fire_achievements[target_type]['years']
                fire_age = fire_achievements[target_type]['age']
                legend_label = f"{target_data['name']} (${target_value:,.0f}) - {years_to_fire:.1f}y @ age {fire_age:.0f}"
            else:
                legend_label = f"{target_data['name']} (${target_value:,.0f}) - Not achieved in timeframe"
            
            # Add invisible trace for legend
            fig.add_trace(go.Scatter(
                x=[None], y=[None],
                mode='lines',
                name=legend_label,
                line=dict(color=fire_colors[target_type], width=line_width, dash=line_dash),
                showlegend=True
            ))
            
            # Add the actual horizontal line
            fig.add_hline(
                y=target_value,
                line_dash=line_dash,
                line_color=fire_colors[target_type],
                line_width=line_width,
                annotation_text="",  # Remove annotation to avoid overlap with legend
            )
    
    fig.update_layout(
        title="Portfolio Growth Over Time with FIRE Targets",
        xaxis_title="Age",
        yaxis_title="Portfolio Value ($)",
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.01,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1
        ),
        margin=dict(r=150)  # Add right margin for legend
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Scenarios Analysis (moved above table for better workflow)
    st.subheader("Scenario Analysis")
    
    scenario_type = st.selectbox(
        "Select Scenario",
        ["No Additional Contributions", "Part-Time Work", "Barista FIRE"]
    )
    
    if scenario_type == "No Additional Contributions":
        if st.button("Run No Contributions Scenario"):
            no_contrib_projections = st.session_state.calculator.generate_no_contribution_projections(
                life_expectancy - current_age
            )
            
            # Store scenario data for table display
            st.session_state.current_scenario = {
                'type': 'no_contributions',
                'data': no_contrib_projections
            }
            
            # Create comparison chart
            fig_scenario = go.Figure()
            
            fig_scenario.add_trace(go.Scatter(
                x=projections_df['age'],
                y=projections_df['portfolio_value'],
                mode='lines',
                name='With Contributions',
                line=dict(color='blue', width=3)
            ))
            
            no_contrib_df = pd.DataFrame(no_contrib_projections)
            fig_scenario.add_trace(go.Scatter(
                x=no_contrib_df['age'],
                y=no_contrib_df['portfolio_value'],
                mode='lines',
                name='No Contributions',
                line=dict(color='red', width=3, dash='dash')
            ))
            
            # Add FIRE target line
            fig_scenario.add_hline(
                y=st.session_state.target_portfolio,
                line_dash="dot",
                line_color="green",
                annotation_text=f"FIRE Target: ${st.session_state.target_portfolio:,.0f}"
            )
            
            # Highlight FIRE achievement points
            fire_achieved_contrib = projections_df[projections_df['fire_achieved'] == True]
            fire_achieved_no_contrib = no_contrib_df[no_contrib_df['fire_achieved'] == True]
            
            if not fire_achieved_contrib.empty:
                first_fire_contrib = fire_achieved_contrib.iloc[0]
                fig_scenario.add_scatter(
                    x=[first_fire_contrib['age']], 
                    y=[first_fire_contrib['portfolio_value']],
                    mode='markers',
                    marker=dict(color='blue', size=12, symbol='star'),
                    name=f'FIRE @ {first_fire_contrib["age"]:.0f} (With Contributions)',
                    showlegend=True
                )
            
            if not fire_achieved_no_contrib.empty:
                first_fire_no_contrib = fire_achieved_no_contrib.iloc[0]
                fig_scenario.add_scatter(
                    x=[first_fire_no_contrib['age']], 
                    y=[first_fire_no_contrib['portfolio_value']],
                    mode='markers',
                    marker=dict(color='red', size=12, symbol='star'),
                    name=f'FIRE @ {first_fire_no_contrib["age"]:.0f} (No Contributions)',
                    showlegend=True
                )
                st.success(f"🎉 FIRE achieved at age {first_fire_no_contrib['age']:.0f} with no additional contributions!")
            else:
                st.warning("⚠️ FIRE not achieved within the projected timeframe with no contributions.")
            
            fig_scenario.update_layout(
                title="Scenario Comparison: With vs Without Contributions",
                xaxis_title="Age",
                yaxis_title="Portfolio Value ($)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_scenario, use_container_width=True)
    
    elif scenario_type == "Part-Time Work":
        col1, col2 = st.columns(2)
        with col1:
            reduced_spending = st.number_input("Reduced Annual Spending ($)", min_value=0, value=int(expected_annual_spending * 0.8), step=1000)
            part_time_income = st.number_input("Part-Time Annual Income ($)", min_value=0, value=20000, step=1000)
        
        with col2:
            part_time_start_age = st.number_input("Part-Time Start Age", min_value=current_age, max_value=100, value=55)
            part_time_end_age = st.number_input("Part-Time End Age", min_value=part_time_start_age, max_value=100, value=62)
        
        if st.button("Run Part-Time Scenario"):
            part_time_projections = st.session_state.calculator.generate_part_time_projections(
                reduced_spending, part_time_income, part_time_start_age, part_time_end_age,
                life_expectancy - current_age
            )
            
            # Store scenario data for table display
            st.session_state.current_scenario = {
                'type': 'part_time',
                'data': part_time_projections
            }
            
            # Create comparison chart
            fig_scenario = go.Figure()
            
            fig_scenario.add_trace(go.Scatter(
                x=projections_df['age'],
                y=projections_df['portfolio_value'],
                mode='lines',
                name='Regular Plan',
                line=dict(color='blue', width=3)
            ))
            
            part_time_df = pd.DataFrame(part_time_projections)
            fig_scenario.add_trace(go.Scatter(
                x=part_time_df['age'],
                y=part_time_df['portfolio_value'],
                mode='lines',
                name='Part-Time Plan',
                line=dict(color='green', width=3, dash='dash')
            ))
            
            # Add FIRE target line
            fig_scenario.add_hline(
                y=st.session_state.target_portfolio,
                line_dash="dot",
                line_color="orange",
                annotation_text=f"FIRE Target: ${st.session_state.target_portfolio:,.0f}"
            )
            
            # Highlight FIRE achievement points
            fire_achieved_regular = projections_df[projections_df['fire_achieved'] == True]
            fire_achieved_part_time = part_time_df[part_time_df['fire_achieved'] == True]
            
            if not fire_achieved_regular.empty:
                first_fire_regular = fire_achieved_regular.iloc[0]
                fig_scenario.add_scatter(
                    x=[first_fire_regular['age']], 
                    y=[first_fire_regular['portfolio_value']],
                    mode='markers',
                    marker=dict(color='blue', size=12, symbol='star'),
                    name=f'FIRE @ {first_fire_regular["age"]:.0f} (Regular Plan)',
                    showlegend=True
                )
            
            if not fire_achieved_part_time.empty:
                first_fire_part_time = fire_achieved_part_time.iloc[0]
                fig_scenario.add_scatter(
                    x=[first_fire_part_time['age']], 
                    y=[first_fire_part_time['portfolio_value']],
                    mode='markers',
                    marker=dict(color='green', size=12, symbol='star'),
                    name=f'FIRE @ {first_fire_part_time["age"]:.0f} (Part-Time Plan)',
                    showlegend=True
                )
                
                # Show comparison of FIRE achievement
                if not fire_achieved_regular.empty:
                    age_diff = first_fire_part_time['age'] - first_fire_regular['age']
                    if age_diff < 0:
                        st.success(f"🎉 Part-time plan achieves FIRE {abs(age_diff):.1f} years earlier at age {first_fire_part_time['age']:.0f}!")
                    elif age_diff > 0:
                        st.info(f"📊 Part-time plan achieves FIRE {age_diff:.1f} years later at age {first_fire_part_time['age']:.0f}")
                    else:
                        st.info(f"📊 Both plans achieve FIRE at the same age: {first_fire_part_time['age']:.0f}")
                else:
                    st.success(f"🎉 FIRE achieved at age {first_fire_part_time['age']:.0f} with part-time work plan!")
            else:
                st.warning("⚠️ FIRE not achieved within the projected timeframe with part-time work plan.")
            
            # Show part-time period visualization
            part_time_periods = part_time_df[part_time_df['is_part_time'] == True]
            if not part_time_periods.empty:
                fig_scenario.add_vrect(
                    x0=part_time_periods['age'].min(),
                    x1=part_time_periods['age'].max(),
                    fillcolor="rgba(255,255,0,0.1)",
                    layer="below",
                    line_width=0,
                    annotation_text="Part-Time Period",
                    annotation_position="top left"
                )
            
            fig_scenario.update_layout(
                title="Scenario Comparison: Regular vs Part-Time Work",
                xaxis_title="Age",
                yaxis_title="Portfolio Value ($)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_scenario, use_container_width=True)
    
    elif scenario_type == "Barista FIRE":
        col1, col2 = st.columns(2)
        with col1:
            barista_annual_income = st.number_input("Annual Barista Job Income ($)", min_value=0, value=30000, step=1000)
            barista_start_age = st.number_input("Barista FIRE Start Age", min_value=current_age, max_value=100, value=50)
        
        with col2:
            barista_end_age = st.number_input("Healthcare Coverage End Age", min_value=barista_start_age, max_value=100, value=65)
            barista_spending = st.number_input("Annual Spending During Barista Period ($)", min_value=0, value=int(expected_annual_spending * 0.9), step=1000)
        
        if st.button("Run Barista FIRE Scenario"):
            # Barista FIRE is essentially part-time work with different framing
            barista_projections = st.session_state.calculator.generate_part_time_projections(
                barista_spending, barista_annual_income, barista_start_age, barista_end_age,
                life_expectancy - current_age
            )
            
            # Store scenario data for table display
            st.session_state.current_scenario = {
                'type': 'barista_fire',
                'data': barista_projections
            }
            
            # Create comparison chart
            fig_scenario = go.Figure()
            
            fig_scenario.add_trace(go.Scatter(
                x=projections_df['age'],
                y=projections_df['portfolio_value'],
                mode='lines',
                name='Regular Plan',
                line=dict(color='blue', width=3)
            ))
            
            barista_df = pd.DataFrame(barista_projections)
            fig_scenario.add_trace(go.Scatter(
                x=barista_df['age'],
                y=barista_df['portfolio_value'],
                mode='lines',
                name='Barista FIRE Plan',
                line=dict(color='purple', width=3, dash='dash')
            ))
            
            # Add FIRE target line
            fig_scenario.add_hline(
                y=st.session_state.target_portfolio,
                line_dash="dot",
                line_color="orange",
                annotation_text=f"FIRE Target: ${st.session_state.target_portfolio:,.0f}"
            )
            
            # Highlight FIRE achievement points
            fire_achieved_regular = projections_df[projections_df['fire_achieved'] == True]
            fire_achieved_barista = barista_df[barista_df['fire_achieved'] == True]
            
            if not fire_achieved_regular.empty:
                first_fire_regular = fire_achieved_regular.iloc[0]
                fig_scenario.add_scatter(
                    x=[first_fire_regular['age']], 
                    y=[first_fire_regular['portfolio_value']],
                    mode='markers',
                    marker=dict(color='blue', size=12, symbol='star'),
                    name=f'FIRE @ {first_fire_regular["age"]:.0f} (Regular Plan)',
                    showlegend=True
                )
            
            if not fire_achieved_barista.empty:
                first_fire_barista = fire_achieved_barista.iloc[0]
                fig_scenario.add_scatter(
                    x=[first_fire_barista['age']], 
                    y=[first_fire_barista['portfolio_value']],
                    mode='markers',
                    marker=dict(color='purple', size=12, symbol='star'),
                    name=f'FIRE @ {first_fire_barista["age"]:.0f} (Barista FIRE)',
                    showlegend=True
                )
                
                # Show comparison of FIRE achievement
                if not fire_achieved_regular.empty:
                    age_diff = first_fire_barista['age'] - first_fire_regular['age']
                    if age_diff < 0:
                        st.success(f"🎉 Barista FIRE plan achieves FIRE {abs(age_diff):.1f} years earlier at age {first_fire_barista['age']:.0f}!")
                    elif age_diff > 0:
                        st.info(f"📊 Barista FIRE plan achieves FIRE {age_diff:.1f} years later at age {first_fire_barista['age']:.0f}")
                    else:
                        st.info(f"📊 Both plans achieve FIRE at the same age: {first_fire_barista['age']:.0f}")
                else:
                    st.success(f"🎉 FIRE achieved at age {first_fire_barista['age']:.0f} with Barista FIRE plan!")
            else:
                st.warning("⚠️ FIRE not achieved within the projected timeframe with Barista FIRE plan.")
            
            # Show barista work period visualization
            barista_periods = barista_df[barista_df['is_part_time'] == True]
            if not barista_periods.empty:
                fig_scenario.add_vrect(
                    x0=barista_periods['age'].min(),
                    x1=barista_periods['age'].max(),
                    fillcolor="rgba(128,0,128,0.1)",
                    layer="below",
                    line_width=0,
                    annotation_text="Barista FIRE Period",
                    annotation_position="top left"
                )
            
            fig_scenario.update_layout(
                title="Scenario Comparison: Regular vs Barista FIRE",
                xaxis_title="Age",
                yaxis_title="Portfolio Value ($)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_scenario, use_container_width=True)
            
            st.info("💡 **Barista FIRE**: Work a lower-stress job that provides healthcare benefits while your portfolio continues growing until you reach full FIRE.")
    
    # Detailed Projections Table
    st.subheader("Detailed Yearly Projections")
    
    # Use scenario data if available, otherwise use original projections
    if 'current_scenario' in st.session_state:
        scenario_data = st.session_state.current_scenario
        display_data = pd.DataFrame(scenario_data['data'])
        scenario_titles = {
            'no_contributions': "No Contributions Scenario",
            'part_time': "Part-Time Work Scenario", 
            'barista_fire': "Barista FIRE Scenario"
        }
        scenario_title = scenario_titles.get(scenario_data['type'], "Unknown Scenario")
        st.write(f"**Currently showing: {scenario_title}**")
    else:
        display_data = projections_df.copy()
        st.write("**Currently showing: Original Plan**")
    
    # Format the projections for display
    display_projections = display_data.copy()
    display_projections['Total Portfolio'] = display_projections['portfolio_value'].apply(lambda x: f"${x:,.0f}")
    display_projections['Target Portfolio'] = display_projections['target_portfolio'].apply(lambda x: f"${x:,.0f}")
    display_projections['Annual Spending'] = display_projections['inflation_adjusted_spending'].apply(lambda x: f"${x:,.0f}")
    
    # Base columns to display
    display_cols = ['age', 'Total Portfolio', 'Target Portfolio', 'Annual Spending']
    column_names = ['Age', 'Portfolio Value', 'Target Portfolio', 'Annual Spending']
    
    # Add contribution column if available - show $0 during retirement years
    if 'annual_contribution' in display_projections.columns:
        def format_contribution(row):
            current_person_age = row['age']
            contribution = row['annual_contribution']
            
            # If person has reached desired retirement age or achieved FIRE, no more contributions
            if desired_retirement_age is not None and current_person_age >= desired_retirement_age:
                return "$0"
            elif row.get('fire_achieved', False):
                return "$0"
            else:
                return f"${contribution:,.0f}"
        
        display_projections['Annual Contribution'] = display_projections.apply(format_contribution, axis=1)
        display_cols.append('Annual Contribution')
        column_names.append('Annual Contribution')
    
    # Add part-time income column if available (for part-time and barista scenarios)
    if 'part_time_income' in display_projections.columns:
        income_label = "Barista Income" if 'current_scenario' in st.session_state and st.session_state.current_scenario['type'] == 'barista_fire' else "Part-Time Income"
        display_projections[income_label] = display_projections['part_time_income'].apply(lambda x: f"${x:,.0f}")
        display_cols.append(income_label)
        column_names.append(income_label)
    
    # Add Social Security income column if available
    if 'social_security_income' in display_projections.columns:
        display_projections['Social Security'] = display_projections['social_security_income'].apply(lambda x: f"${x:,.0f}")
        display_cols.append('Social Security')
        column_names.append('Social Security')
    
    # Add Large Expense columns if available - show funding breakdown
    if 'total_expense' in display_projections.columns:
        # Show contribution reduction if there are any
        if display_projections['contribution_reduction'].sum() > 0:
            display_projections['Contribution Reduction'] = display_projections['contribution_reduction'].apply(lambda x: f"${x:,.0f}" if x > 0 else "$0")
            display_cols.append('Contribution Reduction')
            column_names.append('Contribution Reduction')
        
        # Show portfolio withdrawal if there are any
        if display_projections['portfolio_withdrawal'].sum() > 0:
            display_projections['Portfolio Withdrawal'] = display_projections['portfolio_withdrawal'].apply(lambda x: f"${x:,.0f}" if x > 0 else "$0")
            display_cols.append('Portfolio Withdrawal')
            column_names.append('Portfolio Withdrawal')
        
        # Show total expense amount
        display_projections['Total Large Expense'] = display_projections['total_expense'].apply(lambda x: f"${x:,.0f}" if x > 0 else "$0")
        display_cols.append('Total Large Expense')
        column_names.append('Total Large Expense')
    elif 'large_expense' in display_projections.columns:
        # Fallback for older data format
        display_projections['Large Expense'] = display_projections['large_expense'].apply(lambda x: f"${x:,.0f}" if x > 0 else "$0")
        display_cols.append('Large Expense')
        column_names.append('Large Expense')
    
    # Add required withdrawal column - only show during retirement years
    def calculate_required_withdrawal(row):
        # Only show withdrawal if person has achieved FIRE AND reached retirement age
        current_person_age = row['age']
        has_achieved_fire = row.get('fire_achieved', False)
        
        # Must have achieved FIRE to start withdrawing
        if not has_achieved_fire:
            return "$0"
            
        # Also check desired retirement age if specified
        if desired_retirement_age is not None and current_person_age < desired_retirement_age:
            return "$0"  # Wait until desired retirement age even if FIRE is achieved
            
        # Calculate withdrawal amount based on available columns
        if 'net_withdrawal_needed' in row:
            # For scenarios with part-time income
            withdrawal_amount = row['net_withdrawal_needed']
        elif 'net_spending_need' in row:
            # For other scenarios (after social security)
            withdrawal_amount = row['net_spending_need']
        else:
            # Fallback: use inflation adjusted spending
            withdrawal_amount = row['inflation_adjusted_spending']
            
        return f"${withdrawal_amount:,.0f}"
    
    display_projections['Required Withdrawal'] = display_projections.apply(calculate_required_withdrawal, axis=1)
    display_cols.append('Required Withdrawal')
    column_names.append('Required Withdrawal')
    
    # Add FIRE achieved column with emoji styling
    def format_fire_achieved(row):
        current_person_age = row['age']
        has_achieved_fire = row.get('fire_achieved', False)
        
        # Check if ready for withdrawals (same logic as withdrawal calculation)
        ready_for_retirement = has_achieved_fire
        if desired_retirement_age is not None and current_person_age < desired_retirement_age:
            ready_for_retirement = False
            
        if ready_for_retirement:
            return "✅🔥"  # Checkmark + fire emoji - ready to retire
        elif has_achieved_fire:
            return "🔥⏰"  # Fire achieved but waiting for desired retirement age
        else:
            return "⏳"    # Hourglass for pending FIRE achievement
    
    display_projections['FIRE Status'] = display_projections.apply(format_fire_achieved, axis=1)
    display_cols.append('FIRE Status')
    column_names.append('FIRE Status')
    
    # Select and rename columns
    display_projections = display_projections[display_cols]
    display_projections.columns = column_names
    
    st.dataframe(display_projections, use_container_width=True)
    
    # Add button to reset to original view
    if 'current_scenario' in st.session_state:
        if st.button("Reset to Original Plan View"):
            del st.session_state.current_scenario
            st.rerun()
    
    # Retirement Income Sources Visualization
    st.subheader("Retirement Income Sources")
    
    # Use current data (scenario or original)
    current_data = display_data.copy()
    
    # Filter to retirement years only
    retirement_data = []
    for _, row in current_data.iterrows():
        current_person_age = row['age']
        has_achieved_fire = row.get('fire_achieved', False)
        
        # Check if in retirement
        is_retired = False
        if desired_retirement_age is not None:
            is_retired = current_person_age >= desired_retirement_age
        else:
            is_retired = has_achieved_fire
            
        if is_retired:
            retirement_data.append(row)
    
    if retirement_data:
        retirement_df = pd.DataFrame(retirement_data)
        
        # Create stacked area chart for income sources
        fig_sources = go.Figure()
        
        # Calculate withdrawal sources (simplified - assume equal split between taxable/tax-deferred for now)
        ages = retirement_df['age'].tolist()
        
        # Social Security income
        social_security = retirement_df.get('social_security_income', [0] * len(ages)).tolist()
        
        # Part-time/Barista income (if available)
        part_time_income = []
        if 'part_time_income' in retirement_df.columns:
            part_time_income = retirement_df['part_time_income'].tolist()
        else:
            part_time_income = [0] * len(ages)
        
        # Portfolio withdrawals (Required Withdrawal minus other income sources)
        portfolio_withdrawals = []
        for i, row in retirement_df.iterrows():
            if 'net_withdrawal_needed' in row:
                withdrawal = max(0, row['net_withdrawal_needed'])
            elif 'net_spending_need' in row:
                withdrawal = max(0, row['net_spending_need'])
            else:
                withdrawal = max(0, row['inflation_adjusted_spending'] - row.get('social_security_income', 0) - row.get('part_time_income', 0))
            portfolio_withdrawals.append(withdrawal)
        
        # Split portfolio withdrawals between taxable and tax-deferred (simplified assumption)
        # Before social security age: more from taxable, After: more from tax-deferred
        taxable_withdrawals = []
        tax_deferred_withdrawals = []
        
        for i, age in enumerate(ages):
            total_withdrawal = portfolio_withdrawals[i]
            if age < social_security_age:
                # Before SS: 70% taxable, 30% tax-deferred
                taxable_withdrawals.append(total_withdrawal * 0.7)
                tax_deferred_withdrawals.append(total_withdrawal * 0.3)
            else:
                # After SS: 40% taxable, 60% tax-deferred
                taxable_withdrawals.append(total_withdrawal * 0.4)
                tax_deferred_withdrawals.append(total_withdrawal * 0.6)
        
        # Add traces in stacking order
        fig_sources.add_trace(go.Scatter(
            x=ages,
            y=taxable_withdrawals,
            mode='lines',
            stackgroup='one',
            name='Taxable Portfolio',
            line=dict(color='#1f77b4'),
            fill='tonexty'
        ))
        
        fig_sources.add_trace(go.Scatter(
            x=ages,
            y=[t + td for t, td in zip(taxable_withdrawals, tax_deferred_withdrawals)],
            mode='lines',
            stackgroup='one',
            name='Tax-Deferred Portfolio',
            line=dict(color='#ff7f0e'),
            fill='tonexty'
        ))
        
        # Add part-time income if applicable
        if any(income > 0 for income in part_time_income):
            current_stack = [t + td + pt for t, td, pt in zip(taxable_withdrawals, tax_deferred_withdrawals, part_time_income)]
            income_label = "Barista Income" if 'current_scenario' in st.session_state and st.session_state.current_scenario['type'] == 'barista_fire' else "Part-Time Income"
            
            fig_sources.add_trace(go.Scatter(
                x=ages,
                y=current_stack,
                mode='lines',
                stackgroup='one',
                name=income_label,
                line=dict(color='#2ca02c'),
                fill='tonexty'
            ))
            
            # Update base for social security
            base_values = current_stack
        else:
            base_values = [t + td for t, td in zip(taxable_withdrawals, tax_deferred_withdrawals)]
        
        # Add Social Security
        if any(ss > 0 for ss in social_security):
            fig_sources.add_trace(go.Scatter(
                x=ages,
                y=[base + ss for base, ss in zip(base_values, social_security)],
                mode='lines',
                stackgroup='one',
                name='Social Security',
                line=dict(color='#d62728'),
                fill='tonexty'
            ))
        
        fig_sources.update_layout(
            title="Retirement Income Sources by Year",
            xaxis_title="Age",
            yaxis_title="Annual Income ($)",
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.01
            ),
            margin=dict(r=150)
        )
        
        st.plotly_chart(fig_sources, use_container_width=True)
        
        st.info("💡 This chart shows the composition of your retirement income sources. Taxable accounts are typically used first to allow tax-deferred accounts to continue growing.")
    else:
        st.info("📊 Income sources visualization will appear here once you reach retirement age or achieve FIRE.")
    
    # Monte Carlo Simulation
    st.subheader("Monte Carlo Simulation")
    
    col1, col2 = st.columns(2)
    with col1:
        num_simulations = st.number_input("Number of Simulations", min_value=100, max_value=10000, value=1000, step=100)
    with col2:
        simulation_years = st.number_input("Years to Simulate", min_value=5, max_value=50, value=min(30, life_expectancy - current_age))
    
    if st.button("Run Monte Carlo Simulation"):
        with st.spinner("Running Monte Carlo simulation..."):
            monte_carlo_results = st.session_state.calculator.run_monte_carlo_simulation(
                num_simulations, simulation_years
            )
            
            # Display results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Success Rate", f"{monte_carlo_results['success_rate']:.1f}%")
            with col2:
                st.metric("Median Final Value", f"${monte_carlo_results['final_values']['median']:,.0f}")
            with col3:
                st.metric("Mean Final Value", f"${monte_carlo_results['final_values']['mean']:,.0f}")
            
            # Additional metrics
            col4, col5 = st.columns(2)
            with col4:
                st.metric("Target Portfolio", f"${monte_carlo_results['target_portfolio']:,.0f}")
            with col5:
                st.metric("Standard Deviation", f"${monte_carlo_results['final_values']['std']:,.0f}")
            
            # Create percentile chart
            fig_mc = go.Figure()
            years_range = list(range(monte_carlo_results['years'] + 1))
            
            # Add percentile bands
            fig_mc.add_trace(go.Scatter(
                x=years_range, 
                y=monte_carlo_results['percentiles']['p90'],
                mode='lines',
                name='90th Percentile',
                line=dict(color='rgba(0,100,80,0.3)'),
                showlegend=True
            ))
            
            fig_mc.add_trace(go.Scatter(
                x=years_range,
                y=monte_carlo_results['percentiles']['p75'],
                mode='lines',
                name='75th Percentile',
                line=dict(color='rgba(0,100,80,0.5)'),
                fill='tonexty',
                showlegend=True
            ))
            
            fig_mc.add_trace(go.Scatter(
                x=years_range,
                y=monte_carlo_results['percentiles']['p50'],
                mode='lines',
                name='Median (50th)',
                line=dict(color='blue', width=3),
                showlegend=True
            ))
            
            fig_mc.add_trace(go.Scatter(
                x=years_range,
                y=monte_carlo_results['percentiles']['p25'],
                mode='lines',
                name='25th Percentile',
                line=dict(color='rgba(100,0,0,0.5)'),
                fill='tonexty',
                showlegend=True
            ))
            
            fig_mc.add_trace(go.Scatter(
                x=years_range,
                y=monte_carlo_results['percentiles']['p10'],
                mode='lines',
                name='10th Percentile',
                line=dict(color='rgba(100,0,0,0.3)'),
                showlegend=True
            ))
            
            # Add target line
            fig_mc.add_hline(
                y=monte_carlo_results['target_portfolio'],
                line_dash="dash",
                line_color="red",
                annotation_text=f"FIRE Target: ${monte_carlo_results['target_portfolio']:,.0f}"
            )
            
            fig_mc.update_layout(
                title="Monte Carlo Simulation - Portfolio Growth Percentiles",
                xaxis_title="Years",
                yaxis_title="Portfolio Value ($)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_mc, use_container_width=True)

else:
    st.info("👈 Please fill in your financial information in the sidebar and click 'Calculate FIRE Plan' to see your results.")
    
    # Show some example information
    st.subheader("About VIBE FIRE")
    st.markdown("""
    **VIBE FIRE** combines the power of FIRE (Financial Independence, Retire Early) with comprehensive financial visualization and planning tools.
    
    **Three Types of FIRE:**
    - **Lean FIRE**: Retiring with a smaller nest egg, typically requiring more frugal living
    - **Regular FIRE**: The traditional approach following the 4% rule
    - **Fat FIRE**: Retiring with a larger portfolio to maintain a higher standard of living
    
    **The 4% Rule**: A common guideline suggesting you can safely withdraw 4% of your portfolio annually in retirement.
    
    **VIBE FIRE Features:**
    - Interactive portfolio growth projections
    - Monte Carlo simulations for risk analysis
    - Scenario planning for different life paths
    - Comprehensive FIRE target calculations
    """)

# Feedback Section
st.markdown("---")
st.subheader("📝 Share Your Feedback")

def simple_bot_check():
    """Simple arithmetic bot protection"""
    if 'bot_check_answer' not in st.session_state:
        import random
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        st.session_state.bot_check_question = f"{a} + {b}"
        st.session_state.bot_check_answer = a + b
    
    return st.session_state.bot_check_question, st.session_state.bot_check_answer

def submit_feedback(feedback_text, feedback_type, email=None):
    """Submit feedback via webhook or email service"""
    timestamp = datetime.now().isoformat()
    
    # Prepare feedback data
    feedback_data = {
        "timestamp": timestamp,
        "type": feedback_type,
        "feedback": feedback_text,
        "email": email if email else "anonymous",
        "app": "VIBE FIRE Calculator"
    }
    
    # Option 1: Google Sheets via webhook (recommended)
    # Replace with your Google Apps Script webhook URL
    webhook_url = st.secrets.get("FEEDBACK_WEBHOOK_URL", "")
    
    if webhook_url:
        try:
            response = requests.post(webhook_url, json=feedback_data, timeout=10)
            if response.status_code == 200:
                return True, "Feedback submitted successfully!"
            else:
                return False, "Failed to submit feedback. Please try again."
        except Exception as e:
            return False, f"Error submitting feedback: {str(e)}"
    
    # Option 2: Fallback - save to session state (for development)
    if 'feedback_log' not in st.session_state:
        st.session_state.feedback_log = []
    
    st.session_state.feedback_log.append(feedback_data)
    return True, "Feedback received! (Development mode)"

# Feedback form
with st.expander("💡 Help us improve VIBE FIRE", expanded=False):
    st.write("Your feedback helps us make the calculator better for everyone!")
    
    feedback_type = st.selectbox(
        "What type of feedback?",
        ["Feature Request", "Bug Report", "General Feedback", "UI/UX Suggestion"]
    )
    
    feedback_text = st.text_area(
        "Your feedback:",
        placeholder="Tell us what you think or what could be improved...",
        height=100
    )
    
    email = st.text_input(
        "Email (optional):",
        placeholder="your.email@example.com",
        help="Leave blank to submit anonymously"
    )
    
    # Simple bot protection
    question, correct_answer = simple_bot_check()
    user_answer = st.number_input(
        f"Quick check: What is {question}?",
        min_value=0,
        max_value=100,
        value=0,
        help="Simple math to prevent spam"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        submit_button = st.button("Submit Feedback", type="primary")
    
    with col2:
        if submit_button:
            if not feedback_text.strip():
                st.error("Please enter some feedback before submitting.")
            elif user_answer != correct_answer:
                st.error(f"Incorrect answer to {question}. Please try again.")
            else:
                success, message = submit_feedback(feedback_text, feedback_type, email)
                if success:
                    st.success(message)
                    # Reset form
                    del st.session_state.bot_check_answer
                    st.rerun()
                else:
                    st.error(message)

# Setup instructions for webhook (only show in development)
if not st.secrets.get("FEEDBACK_WEBHOOK_URL") and st.secrets.get("DEBUG_MODE", False):
    with st.expander("🔧 Setup Instructions (Admin Only)", expanded=False):
        st.code("""
# Google Apps Script Setup:
# 1. Go to script.google.com
# 2. Create new script with this code:

function doPost(e) {
  var sheet = SpreadsheetApp.openById('YOUR_SHEET_ID').getActiveSheet();
  var data = JSON.parse(e.postData.contents);
  
  sheet.appendRow([
    data.timestamp,
    data.type,
    data.feedback,
    data.email,
    data.app
  ]);
  
  return ContentService.createTextOutput('Success');
}

# 3. Deploy as web app (execute as me, access to anyone)
# 4. Add webhook URL to Streamlit secrets as FEEDBACK_WEBHOOK_URL
        """)
        
        if 'feedback_log' in st.session_state and st.session_state.feedback_log:
            st.write("**Recent Feedback (Dev Mode):**")
            for fb in st.session_state.feedback_log[-5:]:
                st.json(fb)
