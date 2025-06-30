# Large Expense Bug Analysis

## Critical Bugs Found

### 1. **Massive Negative Portfolio Values** 
- **Location**: Line 181 in `fire_calculator.py`
- **Code**: `portfolio_value += windfall_this_year - large_expense_this_year`
- **Bug**: Can drive portfolio to extreme negative values (e.g., -$722,992.57)
- **Impact**: Causes massive negative values in subsequent years due to compound growth on negative balance

### 2. **Negative Annual Contributions**
- **Location**: Lines 136-138 in `fire_calculator.py`
- **Code**: `base_contribution = self.annual_contribution * (1 - reduction)`
- **Bug**: When `contribution_reduction > 1.0`, this creates negative contributions
- **Impact**: Negative contributions actually withdraw money from portfolio, accelerating negative spiral

### 3. **Incorrect Contribution Reduction Timeline**
- **Location**: Line 136 in `fire_calculator.py`
- **Code**: `if self.large_expense and current_age <= self.large_expense.get('target_age', 999):`
- **Bug**: Applies reduction from current age through target age, including expense year
- **Impact**: Reduces contributions during the expense year when you might need them most

### 4. **No Input Validation**
- **Location**: Throughout `fire_calculator.py` and `app.py`
- **Bug**: No validation on `contribution_reduction` values
- **Impact**: Allows nonsensical values like negative reductions or reductions > 100%

## Root Cause Analysis

The bugs stem from three main issues:

1. **Lack of bounds checking** on input parameters
2. **No portfolio floor validation** - portfolio can go arbitrarily negative
3. **Logical error in contribution reduction timeline** - should prepare for expense, not continue during/after

## Scenarios That Trigger Bugs

1. **Large expense > portfolio value** → Massive negative portfolio
2. **contribution_reduction > 1.0** → Negative contributions
3. **contribution_reduction < 0** → Excessive contributions (bonus bug)
4. **Very large expense with high reduction** → Compound negative spiral

## Test Cases That Demonstrate Bugs

```python
# Bug 1: Portfolio goes to -$722,992.57
large_expense = {
    'target_age': 35,
    'amount': 1000000,  # $1M expense on $125K portfolio
    'contribution_reduction': 0.5
}

# Bug 2: Contribution becomes -$12,500
large_expense = {
    'target_age': 35,
    'amount': 50000,
    'contribution_reduction': 1.5  # 150% reduction
}
```

## Recommended Fixes

1. **Add input validation** for contribution_reduction (0 ≤ x ≤ 1)
2. **Add portfolio floor** - prevent portfolio from going below reasonable negative threshold
3. **Fix timeline logic** - apply reduction only BEFORE target_age, not during/after
4. **Add warning system** for large expenses that exceed portfolio capacity