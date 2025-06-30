import math
import numpy as np
from typing import List, Dict, Tuple
try:
    import numpy as np
except ImportError:
    np = None

class FIRECalculator:
    # FIRE type multipliers for spending requirements
    FIRE_TYPES = {
        'lean': {'multiplier': 0.6, 'name': 'Lean FIRE'},
        'coast': {'multiplier': 1.0, 'name': 'Coast FIRE'},
        'barista': {'multiplier': 0.8, 'name': 'Barista FIRE'},
        'regular': {'multiplier': 1.0, 'name': 'Regular FIRE'},
        'fat': {'multiplier': 1.8, 'name': 'Fat FIRE'}
    }
    
    def __init__(self, current_age: int, current_portfolio_taxable: float, 
                 current_portfolio_tax_deferred: float, annual_contribution: float,
                 expected_annual_spending: float, growth_rate: float = 0.07,
                 inflation_rate: float = 0.03, withdrawal_rate: float = 0.04,
                 social_security_income: float = 0, social_security_age: int = 67,
                 desired_retirement_age: int = None, life_expectancy: int = 85,
                 fire_type: str = 'regular', windfalls: List[Dict] = None,
                 large_expense: Dict = None):
        self.current_age = current_age
        self.current_portfolio_taxable = current_portfolio_taxable
        self.current_portfolio_tax_deferred = current_portfolio_tax_deferred
        self.annual_contribution = annual_contribution
        self.expected_annual_spending = expected_annual_spending
        self.growth_rate = growth_rate
        self.inflation_rate = inflation_rate
        self.withdrawal_rate = withdrawal_rate
        self.social_security_income = social_security_income
        self.social_security_age = social_security_age
        self.desired_retirement_age = desired_retirement_age
        self.life_expectancy = life_expectancy
        self.fire_type = fire_type
        self.windfalls = windfalls or []  # List of {'year': int, 'amount': float}
        self.large_expense = large_expense or {}  # {'year': int, 'amount': float, 'contribution_reduction': float}
        
        # Validate large expense to prevent extreme scenarios
        if self.large_expense:
            expense_type = self.large_expense.get('type', 'single')
            
            if expense_type == 'single':
                expense_amount = self.large_expense.get('amount', 0)
                contribution_reduction = self.large_expense.get('contribution_reduction', 0)
                
                # Warn if expense is larger than current portfolio (could cause negative values)
                if expense_amount > self.current_total_portfolio * 2:
                    print(f"Warning: Large expense (${expense_amount:,.0f}) is much larger than current portfolio (${self.current_total_portfolio:,.0f})")
                
                # Ensure contribution reduction doesn't exceed annual contribution
                if contribution_reduction > self.annual_contribution:
                    print(f"Warning: Contribution reduction (${contribution_reduction:,.0f}) exceeds annual contribution (${self.annual_contribution:,.0f})")
                    self.large_expense['contribution_reduction'] = min(contribution_reduction, self.annual_contribution)
                    
            elif expense_type == 'multi':
                annual_amount = self.large_expense.get('annual_amount', 0)
                start_age = self.large_expense.get('start_age', 0)
                end_age = self.large_expense.get('end_age', 0)
                total_expense = annual_amount * (end_age - start_age + 1)
                
                # Warn if total multi-year expense is excessive
                if total_expense > self.current_total_portfolio * 3:
                    print(f"Warning: Multi-year expense total (${total_expense:,.0f}) is much larger than current portfolio (${self.current_total_portfolio:,.0f})")
                
                # Warn if annual amount exceeds annual contribution
                if annual_amount > self.annual_contribution:
                    print(f"Warning: Annual expense amount (${annual_amount:,.0f}) exceeds annual contribution (${self.annual_contribution:,.0f})")
        
    @property
    def current_total_portfolio(self) -> float:
        return self.current_portfolio_taxable + self.current_portfolio_tax_deferred
    
    def calculate_target_portfolio(self, fire_type: str = None) -> float:
        """Calculate the target portfolio value needed for FIRE using the 4% rule (or custom withdrawal rate)"""
        # Use specified fire_type or default to instance fire_type
        target_fire_type = fire_type or self.fire_type
        multiplier = self.FIRE_TYPES.get(target_fire_type, {'multiplier': 1.0})['multiplier']
        
        # Calculate spending requirement for this FIRE type
        adjusted_spending = self.expected_annual_spending * multiplier
        
        # For FIRE calculations, we need the full portfolio since Social Security comes later
        # We'll account for Social Security reduction in the yearly projections when age-appropriate
        return adjusted_spending / self.withdrawal_rate
    
    def calculate_target_portfolio_with_ss(self, fire_type: str = None) -> float:
        """Calculate target portfolio accounting for Social Security (for retirement readiness check)"""
        # Use specified fire_type or default to instance fire_type
        target_fire_type = fire_type or self.fire_type
        multiplier = self.FIRE_TYPES.get(target_fire_type, {'multiplier': 1.0})['multiplier']
        
        # Calculate spending requirement for this FIRE type
        adjusted_spending = self.expected_annual_spending * multiplier
        
        # If social security income is expected, reduce the portfolio requirement
        net_spending_need = adjusted_spending - self.social_security_income
        return max(0, net_spending_need / self.withdrawal_rate)
    
    def calculate_years_to_fire(self) -> int:
        """Calculate the number of years until FIRE is achieved using actual projections"""
        # Generate projections to find when FIRE is actually achieved
        # considering all factors: large expenses, windfalls, complex logic
        projections = self.generate_yearly_projections()
        
        # Find the first year where FIRE is achieved
        for projection in projections:
            if projection['fire_achieved']:
                return projection['year']
        
        # If FIRE is not achieved within the projection timeframe, return None
        # This will be handled by the caller to show "Not Achieved"
        return None
    
    def generate_yearly_projections(self, num_years: int = None) -> List[Dict]:
        """Generate year-by-year portfolio projections"""
        if num_years is None:
            num_years = self.life_expectancy - self.current_age
        
        projections = []
        portfolio_value = self.current_total_portfolio
        base_target_portfolio = self.calculate_target_portfolio()
        
        for year in range(num_years + 1):
            current_age = self.current_age + year
            
            # Adjust target portfolio for inflation to maintain purchasing power
            inflation_adjusted_target = base_target_portfolio * ((1 + self.inflation_rate) ** year)
            
            # Adjust spending for inflation
            inflation_adjusted_spending = self.expected_annual_spending * ((1 + self.inflation_rate) ** year)
            
            # Calculate social security income if age qualifies
            social_security_income = 0
            if current_age >= self.social_security_age:
                social_security_income = self.social_security_income * ((1 + self.inflation_rate) ** year)
            
            # Net spending need after social security
            net_spending_need = inflation_adjusted_spending - social_security_income
            
            # Calculate sustainable withdrawal
            sustainable_withdrawal = portfolio_value * self.withdrawal_rate
            
            # Determine contribution for this year (stop contributions once FIRE is achieved OR desired retirement age is reached)
            reached_desired_retirement = self.desired_retirement_age and current_age >= self.desired_retirement_age
            
            # Calculate large expense and contribution adjustments for this year
            large_expense_this_year = 0
            contribution_reduction = 0
            portfolio_withdrawal_this_year = 0
            
            if self.large_expense:
                expense_type = self.large_expense.get('type', 'single')
                funding_strategy = self.large_expense.get('funding_strategy', 'portfolio_withdrawal')
                
                # Determine if this is an expense year and the expense amount
                expense_amount_this_year = 0
                
                if expense_type == 'single':
                    # Single year expense
                    target_age = self.large_expense.get('target_age', 0)
                    if current_age == target_age:
                        expense_amount_this_year = self.large_expense.get('amount', 0)
                        
                elif expense_type == 'multi':
                    # Multi-year expense
                    start_age = self.large_expense.get('start_age', 0)
                    end_age = self.large_expense.get('end_age', 0)
                    if start_age <= current_age <= end_age:
                        expense_amount_this_year = self.large_expense.get('annual_amount', 0)
                
                # Apply funding strategy if there's an expense this year
                if expense_amount_this_year > 0:
                    if funding_strategy == 'reduce_contributions':
                        # Reduce contributions first, portfolio withdrawal for remainder
                        contribution_reduction = min(expense_amount_this_year, self.annual_contribution)
                        portfolio_withdrawal_this_year = max(0, expense_amount_this_year - contribution_reduction)
                        
                    elif funding_strategy == 'portfolio_withdrawal':
                        # Take entire amount from portfolio
                        portfolio_withdrawal_this_year = expense_amount_this_year
                        contribution_reduction = 0
                        
                    elif funding_strategy == 'mixed_approach':
                        # Use mixed approach with user-defined limits
                        if expense_type == 'single':
                            max_contribution_reduction = self.large_expense.get('max_contribution_reduction', 0)
                        else:
                            max_contribution_reduction = self.large_expense.get('max_annual_contribution_reduction', 0)
                        
                        contribution_reduction = min(expense_amount_this_year, max_contribution_reduction, self.annual_contribution)
                        portfolio_withdrawal_this_year = max(0, expense_amount_this_year - contribution_reduction)
                    
                    # For backward compatibility and display purposes
                    large_expense_this_year = portfolio_withdrawal_this_year
            
            # Check if FIRE is achieved (against inflation-adjusted target)
            # Must have sufficient portfolio AND be able to sustain withdrawals
            fire_achieved = portfolio_value >= inflation_adjusted_target
            
            # Additional check: if we have large expenses ongoing that reduce our effective available portfolio,
            # we should not consider FIRE achieved during those years
            if self.large_expense and portfolio_withdrawal_this_year > 0:
                # If we have a portfolio withdrawal this year, check if remaining portfolio after withdrawal 
                # would still meet FIRE target for sustainable withdrawals
                portfolio_after_expense = portfolio_value - portfolio_withdrawal_this_year
                if portfolio_after_expense < inflation_adjusted_target:
                    fire_achieved = False
            
            # Calculate final contribution for this year
            base_contribution = max(0, self.annual_contribution - contribution_reduction)
            annual_contribution_this_year = 0 if (fire_achieved or reached_desired_retirement) else base_contribution
            
            # Check for windfalls this year
            windfall_this_year = sum(w['amount'] for w in self.windfalls if w.get('age') == current_age)
            
            projections.append({
                'year': year,
                'age': current_age,
                'portfolio_value': round(portfolio_value, 2),
                'target_portfolio': round(inflation_adjusted_target, 2),
                'inflation_adjusted_spending': round(inflation_adjusted_spending, 2),
                'social_security_income': round(social_security_income, 2),
                'net_spending_need': round(net_spending_need, 2),
                'sustainable_withdrawal': round(sustainable_withdrawal, 2),
                'annual_contribution': round(annual_contribution_this_year, 2),
                'part_time_income': 0,  # Always 0 for regular calculations
                'windfall': round(windfall_this_year, 2),
                'large_expense': round(large_expense_this_year, 2),  # Portfolio withdrawal portion
                'contribution_reduction': round(contribution_reduction, 2),
                'portfolio_withdrawal': round(portfolio_withdrawal_this_year, 2),
                'total_expense': round(contribution_reduction + portfolio_withdrawal_this_year, 2),
                'fire_achieved': fire_achieved,
                'surplus_deficit': round(sustainable_withdrawal - net_spending_need, 2)
            })
            
            # Calculate next year's portfolio value
            if year < num_years:
                # Determine if we're in retirement phase (either FIRE achieved OR actively withdrawing)
                in_retirement_phase = fire_achieved or (self.annual_contribution == 0 and net_spending_need > 0)
                
                if in_retirement_phase:
                    # During retirement: grow portfolio and subtract actual withdrawals
                    actual_withdrawal = max(0, net_spending_need)
                    portfolio_value = portfolio_value * (1 + self.growth_rate) - actual_withdrawal
                else:
                    # During accumulation phase: grow portfolio and add contributions
                    portfolio_value = portfolio_value * (1 + self.growth_rate) + annual_contribution_this_year
                
                # Add windfalls and subtract portfolio withdrawals for large expenses
                portfolio_value += windfall_this_year - portfolio_withdrawal_this_year
        
        return projections
    
    def generate_no_contribution_projections(self, num_years: int) -> List[Dict]:
        """Generate projections assuming no additional contributions"""
        projections = []
        portfolio_value = self.current_total_portfolio
        target_portfolio = self.calculate_target_portfolio()
        
        for year in range(num_years + 1):
            current_age = self.current_age + year
            inflation_adjusted_spending = self.expected_annual_spending * ((1 + self.inflation_rate) ** year)
            
            # Calculate social security income if age qualifies
            social_security_income = 0
            if current_age >= self.social_security_age:
                social_security_income = self.social_security_income * ((1 + self.inflation_rate) ** year)
            
            # Net spending need after social security
            net_spending_need = inflation_adjusted_spending - social_security_income
            sustainable_withdrawal = portfolio_value * self.withdrawal_rate
            
            # Check if FIRE is achieved
            fire_achieved = portfolio_value >= target_portfolio
            
            projections.append({
                'year': year,
                'age': current_age,
                'portfolio_value': round(portfolio_value, 2),
                'target_portfolio': round(target_portfolio, 2),
                'inflation_adjusted_spending': round(inflation_adjusted_spending, 2),
                'social_security_income': round(social_security_income, 2),
                'net_spending_need': round(net_spending_need, 2),
                'sustainable_withdrawal': round(sustainable_withdrawal, 2),
                'surplus_deficit': round(sustainable_withdrawal - net_spending_need, 2),
                'fire_achieved': fire_achieved
            })
            
            if year < num_years:
                # Portfolio grows but no new contributions
                portfolio_value = portfolio_value * (1 + self.growth_rate)
        
        return projections
    
    def generate_part_time_projections(self, reduced_spending: float, part_time_income: float, 
                                     part_time_start_age: int, part_time_end_age: int, num_years: int) -> List[Dict]:
        """Generate projections for part-time work scenario with flexible duration"""
        projections = []
        portfolio_value = self.current_total_portfolio
        base_target_portfolio = self.calculate_target_portfolio()
        fire_achieved_year = None
        
        for year in range(num_years + 1):
            current_age = self.current_age + year
            
            # Determine if we're in part-time period
            is_part_time_period = part_time_start_age <= current_age <= part_time_end_age
            
            if is_part_time_period:
                # Part-time period: reduced spending and part-time income
                inflation_adjusted_spending = reduced_spending * ((1 + self.inflation_rate) ** year)
                inflation_adjusted_income = part_time_income * ((1 + self.inflation_rate) ** year)
            else:
                # Normal period: regular spending, no part-time income
                inflation_adjusted_spending = self.expected_annual_spending * ((1 + self.inflation_rate) ** year)
                inflation_adjusted_income = 0
            
            # Calculate social security income if age qualifies
            social_security_income = 0
            if current_age >= self.social_security_age:
                social_security_income = self.social_security_income * ((1 + self.inflation_rate) ** year)
            
            # Calculate target portfolio adjusted for inflation (for display purposes)
            inflation_adjusted_target = base_target_portfolio * ((1 + self.inflation_rate) ** year)
            
            # Check if FIRE is achieved based on current spending power
            # FIRE is achieved when your portfolio can sustain your current real spending needs
            current_spending_target = inflation_adjusted_spending / self.withdrawal_rate
            fire_achieved = portfolio_value >= current_spending_target
            if fire_achieved and fire_achieved_year is None:
                fire_achieved_year = year
            
            # Net spending need after all income sources
            net_spending_need = inflation_adjusted_spending - social_security_income
            total_income = inflation_adjusted_income + social_security_income
            net_withdrawal_needed = max(0, inflation_adjusted_spending - total_income)
            sustainable_withdrawal = portfolio_value * self.withdrawal_rate
            
            # Determine annual contribution (stop once FIRE is achieved OR desired retirement age is reached)
            reached_desired_retirement = self.desired_retirement_age and current_age >= self.desired_retirement_age
            annual_contribution_this_year = 0 if (fire_achieved or reached_desired_retirement) else self.annual_contribution
            
            projections.append({
                'year': year,
                'age': current_age,
                'portfolio_value': round(portfolio_value, 2),
                'target_portfolio': round(inflation_adjusted_target, 2),
                'inflation_adjusted_spending': round(inflation_adjusted_spending, 2),
                'part_time_income': round(inflation_adjusted_income, 2),
                'social_security_income': round(social_security_income, 2),
                'net_spending_need': round(net_spending_need, 2),
                'net_withdrawal_needed': round(net_withdrawal_needed, 2),
                'sustainable_withdrawal': round(sustainable_withdrawal, 2),
                'annual_contribution': round(annual_contribution_this_year, 2),
                'surplus_deficit': round(sustainable_withdrawal - net_withdrawal_needed, 2),
                'fire_achieved': fire_achieved,
                'fire_achieved_year': fire_achieved_year,
                'is_part_time': is_part_time_period
            })
            
            if year < num_years:
                # Portfolio grows based on net cash flow and current situation
                if fire_achieved:
                    # During retirement: grow portfolio and subtract withdrawals
                    actual_withdrawal = max(0, net_withdrawal_needed)
                    portfolio_value = portfolio_value * (1 + self.growth_rate) - actual_withdrawal
                elif is_part_time_period:
                    # During part-time: regular contributions plus any surplus from part-time income
                    net_cash_flow = total_income - inflation_adjusted_spending
                    portfolio_value = portfolio_value * (1 + self.growth_rate) + annual_contribution_this_year + max(0, net_cash_flow)
                else:
                    # During normal accumulation: add regular contributions
                    portfolio_value = portfolio_value * (1 + self.growth_rate) + annual_contribution_this_year
        
        return projections
    
    def calculate_scenarios(self) -> Dict:
        """Calculate various scenarios for comparison"""
        scenarios = {}
        
        # Conservative scenario (lower growth, higher inflation)
        conservative_calc = FIRECalculator(
            self.current_age, self.current_portfolio_taxable, self.current_portfolio_tax_deferred,
            self.annual_contribution, self.expected_annual_spending,
            growth_rate=0.05, inflation_rate=0.04, withdrawal_rate=self.withdrawal_rate
        )
        scenarios['conservative'] = {
            'years_to_fire': conservative_calc.calculate_years_to_fire(),
            'target_portfolio': conservative_calc.calculate_target_portfolio()
        }
        
        # Optimistic scenario (higher growth, lower inflation)
        optimistic_calc = FIRECalculator(
            self.current_age, self.current_portfolio_taxable, self.current_portfolio_tax_deferred,
            self.annual_contribution, self.expected_annual_spending,
            growth_rate=0.09, inflation_rate=0.02, withdrawal_rate=self.withdrawal_rate
        )
        scenarios['optimistic'] = {
            'years_to_fire': optimistic_calc.calculate_years_to_fire(),
            'target_portfolio': optimistic_calc.calculate_target_portfolio()
        }
        
        # Higher contribution scenario (+50% contributions)
        higher_contrib_calc = FIRECalculator(
            self.current_age, self.current_portfolio_taxable, self.current_portfolio_tax_deferred,
            self.annual_contribution * 1.5, self.expected_annual_spending,
            self.growth_rate, self.inflation_rate, self.withdrawal_rate
        )
        scenarios['higher_contributions'] = {
            'years_to_fire': higher_contrib_calc.calculate_years_to_fire(),
            'target_portfolio': higher_contrib_calc.calculate_target_portfolio()
        }
        
        return scenarios
    
    def calculate_all_fire_targets(self) -> Dict:
        """Calculate target portfolios for all FIRE types"""
        targets = {}
        for fire_type, info in self.FIRE_TYPES.items():
            targets[fire_type] = {
                'target_portfolio': self.calculate_target_portfolio(fire_type),
                'name': info['name'],
                'multiplier': info['multiplier'],
                'annual_spending': self.expected_annual_spending * info['multiplier']
            }
        return targets
    
    def check_retirement_readiness(self) -> Dict:
        """Check if user is on track for their desired retirement age"""
        if self.desired_retirement_age is None:
            return {'on_track': None, 'message': 'No desired retirement age specified'}
        
        years_to_desired_retirement = self.desired_retirement_age - self.current_age
        if years_to_desired_retirement <= 0:
            return {'on_track': False, 'message': 'Desired retirement age is in the past or current'}
        
        # Calculate portfolio value at desired retirement age
        portfolio_at_retirement = self.current_total_portfolio
        for year in range(years_to_desired_retirement):
            portfolio_at_retirement = portfolio_at_retirement * (1 + self.growth_rate) + self.annual_contribution
        
        # Use Social Security adjusted target if retiring at or after SS age
        if self.desired_retirement_age >= self.social_security_age and self.social_security_income > 0:
            target_portfolio = self.calculate_target_portfolio_with_ss()
        else:
            target_portfolio = self.calculate_target_portfolio()
        
        # Check if portfolio will meet target
        on_track = portfolio_at_retirement >= target_portfolio
        shortfall = max(0, target_portfolio - portfolio_at_retirement)
        
        return {
            'on_track': on_track,
            'years_to_desired_retirement': years_to_desired_retirement,
            'portfolio_at_retirement': round(portfolio_at_retirement, 2),
            'target_portfolio': round(target_portfolio, 2),
            'shortfall': round(shortfall, 2),
            'message': f"{'On track' if on_track else 'Not on track'} for retirement at age {self.desired_retirement_age}"
        }
    
    def run_monte_carlo_simulation(self, num_simulations: int = 1000, years: int = 30) -> Dict:
        """Run Monte Carlo simulation for portfolio projections"""
        if np is None:
            return {'error': 'NumPy not available for Monte Carlo simulation'}
        
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # Parameters for simulation
        mean_return = self.growth_rate
        std_return = 0.15  # Assuming 15% standard deviation
        
        results = []
        final_values = []
        
        for sim in range(num_simulations):
            portfolio_value = self.current_total_portfolio
            yearly_values = [portfolio_value]
            
            for year in range(years):
                # Generate random return using normal distribution
                annual_return = np.random.normal(mean_return, std_return)
                
                # Apply return and add contribution
                portfolio_value = portfolio_value * (1 + annual_return) + self.annual_contribution
                yearly_values.append(portfolio_value)
            
            results.append(yearly_values)
            final_values.append(portfolio_value)
        
        # Calculate statistics
        results_array = np.array(results)
        percentiles = np.percentile(results_array, [10, 25, 50, 75, 90], axis=0)
        
        # Calculate probability of success (meeting target portfolio)
        target_portfolio = self.calculate_target_portfolio()
        success_rate = np.mean(np.array(final_values) >= target_portfolio) * 100
        
        return {
            'success_rate': round(success_rate, 1),
            'percentiles': {
                'p10': percentiles[0].tolist(),
                'p25': percentiles[1].tolist(),
                'p50': percentiles[2].tolist(),
                'p75': percentiles[3].tolist(),
                'p90': percentiles[4].tolist()
            },
            'final_values': {
                'mean': round(np.mean(final_values), 2),
                'median': round(np.median(final_values), 2),
                'std': round(np.std(final_values), 2)
            },
            'target_portfolio': target_portfolio,
            'years': years,
            'num_simulations': num_simulations
        }