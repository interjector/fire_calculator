let currentChart = null;
let currentResults = null;
let currentScenarioData = null; // Track current scenario projections

// Form submission handler
document.getElementById('fireForm').addEventListener('submit', function(e) {
    e.preventDefault();
    calculateFIRE();
});

async function calculateFIRE() {
    const formData = new FormData(document.getElementById('fireForm'));
    const data = Object.fromEntries(formData.entries());
    
    // Add windfalls if specified
    if (data.windfall_age && data.windfall_amount) {
        data.windfalls = [{
            age: parseInt(data.windfall_age),
            amount: parseFloat(data.windfall_amount)
        }];
    }
    
    // Add large expense if specified
    if (data.large_expense_age && data.large_expense_amount) {
        data.large_expense = {
            target_age: parseInt(data.large_expense_age),
            amount: parseFloat(data.large_expense_amount),
            contribution_reduction: parseFloat(data.contribution_reduction || 0) / 100
        };
    }

    // Show loading, hide error
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').style.display = 'none';
    document.getElementById('results').style.display = 'none';

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Calculation failed');
        }

        const results = await response.json();
        currentResults = results;
        displayResults(results);

    } catch (error) {
        document.getElementById('error').textContent = 'Error: ' + error.message;
        document.getElementById('error').style.display = 'block';
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function displayResults(results) {
    // Update key metrics
    document.getElementById('targetPortfolio').textContent = formatCurrency(results.target_portfolio);
    document.getElementById('yearsToFire').textContent = results.years_to_fire + ' years';
    document.getElementById('fireAge').textContent = results.fire_age + ' years old';

    // Update retirement readiness status
    if (results.retirement_readiness && results.retirement_readiness.on_track !== null) {
        const status = results.retirement_readiness.on_track ? '✅ On Track' : '⚠️ Behind';
        document.getElementById('retirementStatus').textContent = status;
        document.getElementById('retirementStatus').style.color = results.retirement_readiness.on_track ? '#27ae60' : '#e74c3c';

        // Show retirement readiness details
        displayRetirementReadiness(results.retirement_readiness);
    } else {
        document.getElementById('retirementStatus').textContent = '-';
    }

    // Create portfolio projection chart with FIRE targets
    createPortfolioChart(results.projections, results.fire_targets, results.current_fire_type);

    // Populate detailed table
    populateProjectionTable(results.projections);

    // Display scenario comparison
    displayScenarios(results.scenarios);

    // Show results section
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

function createPortfolioChart(projections, fireTargets, currentFireType) {
    const ctx = document.getElementById('portfolioChart').getContext('2d');

    // Destroy existing chart if it exists
    if (currentChart) {
        currentChart.destroy();
    }

    const years = projections.map(p => p.year);
    const portfolioValues = projections.map(p => p.portfolio_value);
    const targetPortfolio = projections.map(p => p.target_portfolio);
    const sustainableWithdrawal = projections.map(p => p.sustainable_withdrawal);
    const inflationAdjustedSpending = projections.map(p => p.inflation_adjusted_spending);
    const socialSecurityIncome = projections.map(p => p.social_security_income || 0);
    const netSpendingNeed = projections.map(p => p.net_spending_need);

    const datasets = [
        {
            label: 'Portfolio Value',
            data: portfolioValues,
            borderColor: 'rgb(52, 152, 219)',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            tension: 0.1,
            fill: true
        },
        {
            label: 'Target Portfolio (FIRE)',
            data: targetPortfolio,
            borderColor: 'rgb(39, 174, 96)',
            backgroundColor: 'rgba(39, 174, 96, 0.1)',
            borderDash: [5, 5]
        },
        {
            label: 'Sustainable Withdrawal (4%)',
            data: sustainableWithdrawal,
            borderColor: 'rgb(230, 126, 34)',
            backgroundColor: 'rgba(230, 126, 34, 0.1)'
        },
        {
            label: 'Inflation-Adjusted Spending',
            data: inflationAdjustedSpending,
            borderColor: 'rgb(231, 76, 60)',
            backgroundColor: 'rgba(231, 76, 60, 0.1)'
        },
        {
            label: 'Social Security Income',
            data: socialSecurityIncome,
            borderColor: 'rgb(46, 204, 113)',
            backgroundColor: 'rgba(46, 204, 113, 0.1)'
        },
        {
            label: 'Net Spending Need',
            data: netSpendingNeed,
            borderColor: 'rgb(155, 89, 182)',
            backgroundColor: 'rgba(155, 89, 182, 0.1)'
        }
    ];
    
    // Add FIRE target lines for different types if available
    if (fireTargets) {
        const fireColors = {
            'lean': 'rgba(255, 99, 132, 0.8)',
            'coast': 'rgba(54, 162, 235, 0.8)', 
            'barista': 'rgba(255, 206, 86, 0.8)',
            'regular': 'rgba(75, 192, 192, 0.8)',
            'fat': 'rgba(153, 102, 255, 0.8)'
        };
        
        Object.entries(fireTargets).forEach(([fireType, info]) => {
            // Only show non-current FIRE types as dashed lines
            if (fireType !== currentFireType) {
                const fireTargetLine = years.map(() => info.target_portfolio);
                datasets.push({
                    label: `${info.name} Target`,
                    data: fireTargetLine,
                    borderColor: fireColors[fireType] || 'rgba(128, 128, 128, 0.8)',
                    backgroundColor: 'transparent',
                    borderDash: [10, 5],
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0
                });
            }
        });
    }

    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years.map(year => `Year ${year}`),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Portfolio Growth and FIRE Timeline'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            }
        }
    });
}

function displayScenarios(scenarios) {
    const container = document.getElementById('scenarioCards');
    container.innerHTML = '';

    const scenarioNames = {
        'conservative': 'Conservative (5% growth, 4% inflation)',
        'optimistic': 'Optimistic (9% growth, 2% inflation)',
        'higher_contributions': 'Higher Contributions (+50%)'
    };

    Object.entries(scenarios).forEach(([key, scenario]) => {
        const card = document.createElement('div');
        card.className = 'scenario-card';
        card.innerHTML = `
            <h4>${scenarioNames[key]}</h4>
            <p><strong>Years to FIRE:</strong> ${scenario.years_to_fire} years</p>
            <p><strong>Target Portfolio:</strong> ${formatCurrency(scenario.target_portfolio)}</p>
        `;
        container.appendChild(card);
    });
}

async function showScenarioAnalysis(scenarioType) {
    const formData = new FormData(document.getElementById('fireForm'));
    const data = Object.fromEntries(formData.entries());
    data.scenario_type = scenarioType;

    try {
        const response = await fetch('/scenario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const results = await response.json();
        createScenarioChart(results.projections, 'No Additional Contributions Scenario');
        
        // Store the current scenario data
        currentScenarioData = results.projections;
        
        // Show return button
        showReturnToOriginalButton();
        
        // Update table if we're on the table tab
        if (document.getElementById('table').classList.contains('active')) {
            populateProjectionTable(results.projections, 'scenario');
        }

    } catch (error) {
        alert('Error calculating scenario: ' + error.message);
    }
}

function showPartTimeModal() {
    document.getElementById('partTimeModal').style.display = 'block';
}

function closePartTimeModal() {
    document.getElementById('partTimeModal').style.display = 'none';
}

async function calculatePartTimeScenario() {
    const formData = new FormData(document.getElementById('fireForm'));
    const data = Object.fromEntries(formData.entries());
    data.scenario_type = 'part_time';

    // Determine spending amount based on user selection
    const spendingOption = document.getElementById('spendingOption').value;
    if (spendingOption === 'same') {
        data.reduced_spending = data.expected_annual_spending;
    } else {
        data.reduced_spending = document.getElementById('customSpending').value;
    }

    data.part_time_income = document.getElementById('partTimeIncome').value;
    data.part_time_start_age = document.getElementById('partTimeStartAge').value;
    data.part_time_end_age = document.getElementById('partTimeEndAge').value;
    
    // Add windfalls if specified
    if (data.windfall_age && data.windfall_amount) {
        data.windfalls = [{
            age: parseInt(data.windfall_age),
            amount: parseFloat(data.windfall_amount)
        }];
    }
    
    // Add large expense if specified
    if (data.large_expense_age && data.large_expense_amount) {
        data.large_expense = {
            target_age: parseInt(data.large_expense_age),
            amount: parseFloat(data.large_expense_amount),
            contribution_reduction: parseFloat(data.contribution_reduction || 0) / 100
        };
    }

    try {
        const response = await fetch('/scenario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const results = await response.json();
        const startAge = data.part_time_start_age;
        const endAge = data.part_time_end_age;
        const duration = endAge - startAge + 1;
        const title = `Part-Time Work: Ages ${startAge}-${endAge} (${duration} years)`;

        createScenarioChart(results.projections, title);
        populateProjectionTable(results.projections, 'part_time');

        // Store the current scenario data
        currentScenarioData = results.projections;

        // Show a button to return to original calculations
        showReturnToOriginalButton();

        closePartTimeModal();

    } catch (error) {
        alert('Error calculating part-time scenario: ' + error.message);
    }
}

function createScenarioChart(projections, title) {
    const ctx = document.getElementById('portfolioChart').getContext('2d');

    if (currentChart) {
        currentChart.destroy();
    }

    const years = projections.map(p => p.year);
    const portfolioValues = projections.map(p => p.portfolio_value);

    const datasets = [
        {
            label: 'Portfolio Value',
            data: portfolioValues,
            borderColor: 'rgb(155, 89, 182)',
            backgroundColor: 'rgba(155, 89, 182, 0.1)',
            fill: true
        }
    ];

    // Add target portfolio line if available (for no contributions scenario)
    if (projections[0].target_portfolio !== undefined) {
        datasets.push({
            label: 'Target Portfolio (FIRE)',
            data: projections.map(p => p.target_portfolio),
            borderColor: 'rgb(39, 174, 96)',
            backgroundColor: 'rgba(39, 174, 96, 0.1)',
            borderDash: [5, 5],
            fill: false
        });
    }

    // Add part-time specific data if available
    if (projections[0].part_time_income !== undefined) {
        datasets.push({
            label: 'Part-Time Income',
            data: projections.map(p => p.part_time_income),
            borderColor: 'rgb(26, 188, 156)',
            backgroundColor: 'rgba(26, 188, 156, 0.1)'
        });
    }
    
    // Find FIRE achievement year for part-time scenarios
    let fireAchievedYear = null;
    for (let i = 0; i < projections.length; i++) {
        const current = projections[i];
        const previous = projections[i - 1];
        if (current.fire_achieved && (!previous || !previous.fire_achieved)) {
            fireAchievedYear = current.year;
            break;
        }
    }

    datasets.push({
        label: 'Sustainable Withdrawal',
        data: projections.map(p => p.sustainable_withdrawal),
        borderColor: 'rgb(230, 126, 34)',
        backgroundColor: 'rgba(230, 126, 34, 0.1)'
    });

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: title
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return formatCurrency(value);
                    }
                }
            }
        }
    };
    
    // Add FIRE achievement vertical line if we found the year
    if (fireAchievedYear !== null) {
        // Create a vertical line using chart.js annotation-like approach
        // We'll add this as a special dataset that creates a vertical line
        const maxValue = Math.max(...portfolioValues) * 1.1; // 10% above max for visibility
        const minValue = 0;
        
        // Create two points to draw a vertical line
        const fireLineData = years.map(year => {
            if (year === fireAchievedYear) {
                return maxValue;
            }
            return null;
        });
        
        datasets.push({
            label: `🔥 FIRE Achieved (Year ${fireAchievedYear})`,
            data: fireLineData,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderWidth: 3,
            pointRadius: 0,
            fill: false,
            showLine: false,
            type: 'line'
        });
        
        // Update chart title to include FIRE achievement info
        chartOptions.plugins.title.text = `${title} - FIRE Achieved at Year ${fireAchievedYear}`;
        
        // Add custom plugins array for the vertical line
        if (!chartOptions.plugins.plugins) {
            chartOptions.plugins.plugins = [];
        }
        chartOptions.plugins.plugins.push({
            afterDraw: function(chart) {
                if (fireAchievedYear !== null) {
                    const ctx = chart.ctx;
                    const xAxis = chart.scales.x;
                    const yAxis = chart.scales.y;
                    
                    const xPosition = xAxis.getPixelForValue(fireAchievedYear);
                    
                    ctx.save();
                    ctx.strokeStyle = 'rgb(255, 99, 132)';
                    ctx.lineWidth = 3;
                    ctx.setLineDash([10, 5]);
                    ctx.beginPath();
                    ctx.moveTo(xPosition, yAxis.top);
                    ctx.lineTo(xPosition, yAxis.bottom);
                    ctx.stroke();
                    ctx.restore();
                    
                    // Add text label
                    ctx.save();
                    ctx.fillStyle = 'rgb(255, 99, 132)';
                    ctx.font = 'bold 12px sans-serif';
                    ctx.textAlign = 'center';
                    ctx.fillText(`FIRE Year ${fireAchievedYear}`, xPosition, yAxis.top - 10);
                    ctx.restore();
                }
            }
        });
    }
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years.map(year => `Year ${year}`),
            datasets: datasets
        },
        options: chartOptions
    });
}

function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Show selected tab content
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked tab
    event.target.classList.add('active');

    // If switching tabs, use current scenario data if available, otherwise original data
    if (tabName === 'projections') {
        if (currentScenarioData) {
            // We're viewing a scenario - use scenario chart
            const scenarioTitle = currentChart?.options?.plugins?.title?.text || 'Scenario Analysis';
            createScenarioChart(currentScenarioData, scenarioTitle);
            populateProjectionTable(currentScenarioData, 'scenario');
        } else if (currentResults) {
            // Original calculation
            createPortfolioChart(currentResults.projections, currentResults.fire_targets, currentResults.current_fire_type);
            populateProjectionTable(currentResults.projections);
            hideReturnToOriginalButton();
        }
    } else if (tabName === 'table') {
        if (currentScenarioData) {
            // We're viewing a scenario - use scenario data
            populateProjectionTable(currentScenarioData, 'scenario');
        } else if (currentResults) {
            // Original calculation
            populateProjectionTable(currentResults.projections);
            hideReturnToOriginalButton();
        }
    }
}

function resetForm() {
    document.getElementById('fireForm').reset();
    document.getElementById('results').style.display = 'none';
    document.getElementById('error').style.display = 'none';

    // Reset form to default values
    document.getElementById('current_age').value = '30';
    document.getElementById('current_portfolio_taxable').value = '50000';
    document.getElementById('current_portfolio_tax_deferred').value = '75000';
    document.getElementById('annual_contribution').value = '25000';
    document.getElementById('expected_annual_spending').value = '60000';
    document.getElementById('growth_rate').value = '7';
    document.getElementById('inflation_rate').value = '3';
    document.getElementById('withdrawal_rate').value = '4';
    document.getElementById('desired_retirement_age').value = '';
    document.getElementById('social_security_income').value = '0';
    document.getElementById('social_security_age').value = '67';
    document.getElementById('life_expectancy').value = '85';
}

function displayRetirementReadiness(readiness) {
    const container = document.getElementById('retirementReadiness');
    const content = document.getElementById('readinessContent');

    if (readiness.on_track !== null) {
        container.style.display = 'block';

        const statusColor = readiness.on_track ? '#27ae60' : '#e74c3c';
        const statusIcon = readiness.on_track ? '✅' : '⚠️';

        content.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                <div>
                    <strong>Status:</strong><br>
                    <span style="color: ${statusColor}; font-size: 18px;">${statusIcon} ${readiness.message}</span>
                </div>
                <div>
                    <strong>Years to Target Retirement:</strong><br>
                    <span style="font-size: 18px;">${readiness.years_to_desired_retirement} years</span>
                </div>
                <div>
                    <strong>Portfolio at Retirement:</strong><br>
                    <span style="font-size: 18px;">${formatCurrency(readiness.portfolio_at_retirement)}</span>
                </div>
                <div>
                    <strong>Target Portfolio:</strong><br>
                    <span style="font-size: 18px;">${formatCurrency(readiness.target_portfolio)}</span>
                </div>
                ${readiness.shortfall > 0 ? `
                <div>
                    <strong>Shortfall:</strong><br>
                    <span style="color: #e74c3c; font-size: 18px;">${formatCurrency(readiness.shortfall)}</span>
                </div>
                ` : ''}
            </div>
        `;
    }
}

async function runMonteCarloSimulation() {
    const formData = new FormData(document.getElementById('fireForm'));
    const data = Object.fromEntries(formData.entries());

    // Add Monte Carlo specific parameters
    data.num_simulations = parseInt(document.getElementById('numSimulations').value);
    data.years = parseInt(document.getElementById('simulationYears').value);

    try {
        const response = await fetch('/monte_carlo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error('Monte Carlo simulation failed');
        }

        const results = await response.json();
        displayMonteCarloResults(results);

    } catch (error) {
        alert('Error running Monte Carlo simulation: ' + error.message);
    }
}

function displayMonteCarloResults(results) {
    const container = document.getElementById('monteCarloResults');
    const summaryDiv = document.getElementById('monteCarloSummary');

    if (results.error) {
        summaryDiv.innerHTML = `<p style="color: #e74c3c;">Error: ${results.error}</p>`;
        container.style.display = 'block';
        return;
    }

    // Display summary statistics
    summaryDiv.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
            <div>
                <strong>Success Rate:</strong><br>
                <span style="font-size: 24px; color: ${results.success_rate >= 80 ? '#27ae60' : results.success_rate >= 60 ? '#f39c12' : '#e74c3c'};">
                    ${results.success_rate}%
                </span>
            </div>
            <div>
                <strong>Simulations Run:</strong><br>
                <span style="font-size: 18px;">${results.num_simulations.toLocaleString()}</span>
            </div>
            <div>
                <strong>Years Simulated:</strong><br>
                <span style="font-size: 18px;">${results.years}</span>
            </div>
            <div>
                <strong>Target Portfolio:</strong><br>
                <span style="font-size: 18px;">${formatCurrency(results.target_portfolio)}</span>
            </div>
            <div>
                <strong>Mean Final Value:</strong><br>
                <span style="font-size: 18px;">${formatCurrency(results.final_values.mean)}</span>
            </div>
            <div>
                <strong>Median Final Value:</strong><br>
                <span style="font-size: 18px;">${formatCurrency(results.final_values.median)}</span>
            </div>
        </div>
    `;

    // Create Monte Carlo chart
    createMonteCarloChart(results);

    container.style.display = 'block';
}

function createMonteCarloChart(results) {
    const ctx = document.getElementById('monteCarloChart').getContext('2d');

    if (currentChart) {
        currentChart.destroy();
    }

    const years = Array.from({length: results.years + 1}, (_, i) => i);

    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years.map(year => `Year ${year}`),
            datasets: [
                {
                    label: '90th Percentile',
                    data: results.percentiles.p90,
                    borderColor: 'rgba(39, 174, 96, 0.8)',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    fill: '+1'
                },
                {
                    label: '75th Percentile',
                    data: results.percentiles.p75,
                    borderColor: 'rgba(52, 152, 219, 0.8)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: '+1'
                },
                {
                    label: 'Median (50th)',
                    data: results.percentiles.p50,
                    borderColor: 'rgba(230, 126, 34, 1)',
                    backgroundColor: 'rgba(230, 126, 34, 0.1)',
                    borderWidth: 3,
                    fill: '+1'
                },
                {
                    label: '25th Percentile',
                    data: results.percentiles.p25,
                    borderColor: 'rgba(231, 76, 60, 0.8)',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: '+1'
                },
                {
                    label: '10th Percentile',
                    data: results.percentiles.p10,
                    borderColor: 'rgba(155, 89, 182, 0.8)',
                    backgroundColor: 'rgba(155, 89, 182, 0.1)',
                    fill: false
                },
                {
                    label: 'Target Portfolio',
                    data: Array(results.years + 1).fill(results.target_portfolio),
                    borderColor: 'rgba(0, 0, 0, 0.8)',
                    backgroundColor: 'rgba(0, 0, 0, 0.1)',
                    borderDash: [10, 5],
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Monte Carlo Simulation (${results.num_simulations.toLocaleString()} runs)`
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function populateProjectionTable(projections, tableType = 'main') {
    const tableBody = document.getElementById('projectionTableBody');
    
    // Part-time income column is now always present in HTML template
    tableBody.innerHTML = '';

    projections.forEach(projection => {
        const row = document.createElement('tr');
        if (projection.fire_achieved) {
            row.classList.add('fire-achieved');
        }
        if (projection.is_part_time) {
            row.style.backgroundColor = '#e8f5e8';
        }

        const annualContribution = formatCurrency(projection.annual_contribution || 0);
        const fireStatus = projection.fire_achieved ? '✅ FIRE' : '⏳ Accumulating';

        // Part-time income (always show column, will be $0 for non-part-time scenarios)
        const partTimeIncome = projection.part_time_income || 0;
        const partTimeStyle = partTimeIncome > 0 ? 'color: #26a69a; font-weight: bold;' : 'color: #999;';
        
        // Additional columns for windfalls and expenses
        const windfall = projection.windfall || 0;
        const largeExpense = projection.large_expense || 0;
        const windfallStyle = windfall > 0 ? 'color: #27ae60; font-weight: bold;' : 'color: #999;';
        const expenseStyle = largeExpense > 0 ? 'color: #e74c3c; font-weight: bold;' : 'color: #999;';
        
        row.innerHTML = `
            <td>${projection.year}</td>
            <td>${projection.age}</td>
            <td>${formatCurrency(projection.portfolio_value)}</td>
            <td>${annualContribution}</td>
            <td>${formatCurrency(projection.sustainable_withdrawal)}</td>
            <td>${formatCurrency(projection.inflation_adjusted_spending || projection.net_spending_need)}</td>
            <td style="${partTimeStyle}">${formatCurrency(partTimeIncome)}</td>
            <td style="${windfallStyle}">${formatCurrency(windfall)}</td>
            <td style="${expenseStyle}">${formatCurrency(largeExpense)}</td>
            <td>${formatCurrency(projection.social_security_income || 0)}</td>
            <td>${formatCurrency(projection.net_spending_need || projection.net_withdrawal_needed || 0)}</td>
            <td style="color: ${projection.surplus_deficit >= 0 ? '#27ae60' : '#e74c3c'};">
                ${projection.surplus_deficit >= 0 ? '+' : ''}${formatCurrency(projection.surplus_deficit)}
            </td>
            <td>${fireStatus}</td>
        `;

        tableBody.appendChild(row);
    });
}

function toggleTablePhase(phase) {
    const rows = document.querySelectorAll('#projectionTableBody tr');

    rows.forEach(row => {
        const fireStatus = row.cells[9].textContent;
        const isAccumulation = fireStatus.includes('Accumulating');
        const isWithdrawal = fireStatus.includes('FIRE');

        if (phase === 'all') {
            row.style.display = '';
        } else if (phase === 'accumulation' && isAccumulation) {
            row.style.display = '';
        } else if (phase === 'withdrawal' && isWithdrawal) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function getCurrentAnnualContribution() {
    return parseFloat(document.getElementById('annual_contribution').value) || 0;
}

function updatePartTimeScenarioSummary() {
    const startAge = document.getElementById('partTimeStartAge').value || 55;
    const endAge = document.getElementById('partTimeEndAge').value || 62;
    const income = document.getElementById('partTimeIncome').value || 40000;
    const duration = endAge - startAge + 1;

    // Update the summary content in the modal
    const summaryDiv = document.getElementById('partTimeScenarioSummary');
    const spendingOption = document.getElementById('spendingOption').value;
    const customSpending = document.getElementById('customSpending').value;
    const retirementSpending = document.getElementById('expected_annual_spending').value;

    let spendingText;
    if (spendingOption === 'same') {
        spendingText = `Same as retirement spending (${formatCurrency(retirementSpending)})`;
    } else {
        spendingText = `Custom amount (${formatCurrency(customSpending || 60000)})`;
    }

    summaryDiv.innerHTML = `
        <p><strong>Period:</strong> Work part-time from age ${startAge} to ${endAge} (${duration} years)</p>
        <p><strong>Income:</strong> ${formatCurrency(income)}/year during part-time period</p>
        <p><strong>Spending:</strong> <span id="spendingSummary">${spendingText}</span></p>
        <p><strong>Net Impact:</strong> <span id="netImpactSummary">Reduces portfolio withdrawals by part-time income</span></p>
    `;
}

function resetPartTimeForm() {
    document.getElementById('partTimeStartAge').value = '55';
    document.getElementById('partTimeEndAge').value = '62';
    document.getElementById('partTimeIncome').value = '40000';
    document.getElementById('spendingOption').value = 'same';
    document.getElementById('customSpending').value = '60000';
    toggleSpendingInput();
    updatePartTimeScenarioSummary();
}

// Toggle custom spending input visibility
function toggleSpendingInput() {
    const spendingOption = document.getElementById('spendingOption').value;
    const customSpendingGroup = document.getElementById('customSpendingGroup');

    if (spendingOption === 'custom') {
        customSpendingGroup.style.display = 'block';
    } else {
        customSpendingGroup.style.display = 'none';
    }

    updatePartTimeScenarioSummary();
}

// Add event listeners for part-time scenario changes
document.addEventListener('DOMContentLoaded', function() {
    const startAgeInput = document.getElementById('partTimeStartAge');
    const endAgeInput = document.getElementById('partTimeEndAge');
    const incomeInput = document.getElementById('partTimeIncome');
    const spendingSelect = document.getElementById('spendingOption');
    const customSpendingInput = document.getElementById('customSpending');

    if (startAgeInput && endAgeInput) {
        startAgeInput.addEventListener('input', updatePartTimeScenarioSummary);
        endAgeInput.addEventListener('input', updatePartTimeScenarioSummary);
        incomeInput.addEventListener('input', updatePartTimeScenarioSummary);
        spendingSelect.addEventListener('change', function() {
            toggleSpendingInput();
            updatePartTimeScenarioSummary();
        });
        customSpendingInput.addEventListener('input', updatePartTimeScenarioSummary);

        // Initialize the form state
        toggleSpendingInput();
        updatePartTimeScenarioSummary();
    }
});

function showReturnToOriginalButton() {
    let returnButton = document.getElementById('returnToOriginalButton');
    if (!returnButton) {
        returnButton = document.createElement('button');
        returnButton.id = 'returnToOriginalButton';
        returnButton.className = 'btn btn-secondary';
        returnButton.textContent = 'Return to Original Calculations';
        returnButton.onclick = returnToOriginalCalculations;
        returnButton.style.marginBottom = '10px';

        const tableContainer = document.querySelector('#table .table-toggle');
        tableContainer.appendChild(returnButton);
    }
    returnButton.style.display = 'inline-block';
}

function hideReturnToOriginalButton() {
    const returnButton = document.getElementById('returnToOriginalButton');
    if (returnButton) {
        returnButton.style.display = 'none';
    }
}

function returnToOriginalCalculations() {
    if (currentResults) {
        // Clear scenario data and return to original
        currentScenarioData = null;
        createPortfolioChart(currentResults.projections, currentResults.fire_targets, currentResults.current_fire_type);
        populateProjectionTable(currentResults.projections);
        hideReturnToOriginalButton();
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}
