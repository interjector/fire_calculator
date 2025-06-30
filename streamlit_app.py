import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fire_calculator import FIRECalculator
import numpy as np

st.set_page_config(
    page_title="FIRE Calculator",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔥 FIRE Calculator")
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
fire_type = st.sidebar.selectbox("FIRE Type", ["lean", "regular", "fat"])

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
    large_expense = {
        "target_age": st.sidebar.number_input("Age for Large Expense", min_value=current_age, max_value=100, value=current_age+10),
        "amount": st.sidebar.number_input("Large Expense Amount ($)", min_value=0, value=50000, step=1000),
        "contribution_reduction": st.sidebar.number_input("Contribution Reduction During Expense ($)", min_value=0, value=0, step=1000)
    }

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
    st.session_state.fire_age = current_age + st.session_state.years_to_fire
    st.session_state.projections = calculator.generate_yearly_projections()
    st.session_state.scenarios = calculator.calculate_scenarios()
    st.session_state.retirement_readiness = calculator.check_retirement_readiness()
    st.session_state.fire_targets = calculator.calculate_all_fire_targets()

# Display results if available
if 'calculator' in st.session_state:
    # Main results
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Target Portfolio", f"${st.session_state.target_portfolio:,.0f}")
    
    with col2:
        st.metric("Years to FIRE", f"{st.session_state.years_to_fire:.1f}")
    
    with col3:
        st.metric("FIRE Age", f"{st.session_state.fire_age:.0f}")
    
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
        name='Total Portfolio',
        line=dict(color='blue', width=3)
    ))
    
    # Add FIRE target line
    fig.add_hline(
        y=st.session_state.target_portfolio,
        line_dash="dash",
        line_color="red",
        annotation_text=f"FIRE Target: ${st.session_state.target_portfolio:,.0f}"
    )
    
    fig.update_layout(
        title="Portfolio Growth Over Time",
        xaxis_title="Age",
        yaxis_title="Portfolio Value ($)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Projections Table
    st.subheader("Detailed Yearly Projections")
    
    # Format the projections for display
    display_projections = projections_df.copy()
    display_projections['Total Portfolio'] = display_projections['portfolio_value'].apply(lambda x: f"${x:,.0f}")
    display_projections['Target Portfolio'] = display_projections['target_portfolio'].apply(lambda x: f"${x:,.0f}")
    display_projections['Annual Spending'] = display_projections['inflation_adjusted_spending'].apply(lambda x: f"${x:,.0f}")
    display_projections['Annual Contribution'] = display_projections['annual_contribution'].apply(lambda x: f"${x:,.0f}")
    
    # Select columns to display
    display_cols = ['age', 'Total Portfolio', 'Target Portfolio', 'Annual Spending', 'Annual Contribution', 'fire_achieved']
    display_projections = display_projections[display_cols]
    display_projections.columns = ['Age', 'Portfolio Value', 'Target Portfolio', 'Annual Spending', 'Annual Contribution', 'FIRE Achieved']
    
    st.dataframe(display_projections, use_container_width=True)
    
    # Scenarios Analysis
    st.subheader("Scenario Analysis")
    
    scenario_type = st.selectbox(
        "Select Scenario",
        ["No Additional Contributions", "Part-Time Work"]
    )
    
    if scenario_type == "No Additional Contributions":
        if st.button("Run No Contributions Scenario"):
            no_contrib_projections = st.session_state.calculator.generate_no_contribution_projections(
                life_expectancy - current_age
            )
            
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
            
            fig_scenario.update_layout(
                title="Scenario Comparison: Regular vs Part-Time Work",
                xaxis_title="Age",
                yaxis_title="Portfolio Value ($)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_scenario, use_container_width=True)
    
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
    st.subheader("About FIRE")
    st.markdown("""
    **FIRE** stands for **Financial Independence, Retire Early**. It's a movement focused on extreme saving and investing to allow for early retirement.
    
    **Three Types of FIRE:**
    - **Lean FIRE**: Retiring with a smaller nest egg, typically requiring more frugal living
    - **Regular FIRE**: The traditional approach following the 4% rule
    - **Fat FIRE**: Retiring with a larger portfolio to maintain a higher standard of living
    
    **The 4% Rule**: A common guideline suggesting you can safely withdraw 4% of your portfolio annually in retirement.
    """)