// Financial Advisor Assistant - JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize charts if on results page
    if (document.getElementById('growthChart')) {
        initializeGrowthChart();
        // Update advice source message after charts are initialized
        setTimeout(updateAdviceSourceMessage, 100);
    }
    
    // Add loading states to form submission
    const form = document.getElementById('financialForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            showLoadingState();
        });
    }
    
    // Handle custom financial goal field
    const financialGoalSelect = document.getElementById('financial_goal');
    const customGoalField = document.getElementById('financial_goal_custom');
    
    if (financialGoalSelect && customGoalField) {
        financialGoalSelect.addEventListener('change', function() {
            if (this.value === 'Other') {
                customGoalField.style.display = 'block';
                customGoalField.required = true;
            } else {
                customGoalField.style.display = 'none';
                customGoalField.required = false;
                customGoalField.value = '';
            }
        });
    }
    
    // Handle custom fields for savings, income, and expenses
    setupCustomFields('current_savings', 'current_savings_custom');
    setupCustomFields('monthly_income', 'monthly_income_custom');
    setupCustomFields('monthly_expenses', 'monthly_expenses_custom');
});

function initializeFormValidation() {
    const form = document.getElementById('financialForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Remove existing error styling
    clearFieldError(field);
    
    // Check if field is required
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Specific validation for different field types
    if (field.type === 'number' && value) {
        const numValue = parseFloat(value);
        if (isNaN(numValue) || numValue < 0) {
            isValid = false;
            errorMessage = 'Please enter a valid positive number';
        }
    }
    
    if (field.name === 'timeframe' && value) {
        const numValue = parseInt(value);
        if (isNaN(numValue) || numValue <= 0 || numValue > 100) {
            isValid = false;
            errorMessage = 'Please enter a valid timeframe (1-100 years)';
        }
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.color = 'var(--text-secondary)';
    errorDiv.style.fontSize = '0.875rem';
    errorDiv.style.marginTop = '0.25rem';
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function showLoadingState() {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.innerHTML = '<span class="loading"></span> Generating Advice...';
        submitBtn.disabled = true;
    }
}

function initializeGrowthChart() {
    const ctx = document.getElementById('growthChart');
    if (!ctx) {
        console.log('Chart canvas not found');
        return;
    }
    
    // Get data from the page - parse carefully
    const timeframeElement = document.getElementById('timeframeData');
    const currentSavingsElement = document.getElementById('currentSavingsData');
    const monthlyIncomeElement = document.getElementById('monthlyIncomeData');
    const monthlyExpensesElement = document.getElementById('monthlyExpensesData');
    
    if (!timeframeElement || !currentSavingsElement || !monthlyIncomeElement || !monthlyExpensesElement) {
        console.log('Chart data elements not found');
        return;
    }
    
    const timeframe = parseInt(timeframeElement.textContent.trim());
    const currentSavings = parseFloat(currentSavingsElement.textContent.trim());
    const monthlyIncome = parseFloat(monthlyIncomeElement.textContent.trim());
    const monthlyExpenses = parseFloat(monthlyExpensesElement.textContent.trim());
    
    console.log('Chart data:', { timeframe, currentSavings, monthlyIncome, monthlyExpenses });
    
    // Validate data
    if (isNaN(timeframe) || isNaN(currentSavings) || isNaN(monthlyIncome) || isNaN(monthlyExpenses)) {
        console.error('Invalid chart data');
        return;
    }
    
    // Calculate projected growth scenarios
    const scenarios = calculateGrowthScenarios(timeframe, currentSavings, monthlyIncome, monthlyExpenses);
    console.log('Scenarios:', scenarios);
    
    // Update chart insights
    updateChartInsights(timeframe, currentSavings, monthlyIncome, monthlyExpenses);
    
    // Create Chart.js chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: scenarios.labels,
            datasets: [
                {
                    label: 'Current Path (Savings Only)',
                    data: scenarios.currentPath,
                    borderColor: '#8E8E93',
                    backgroundColor: 'rgba(142, 142, 147, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.2,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    borderDash: [3, 3]
                },
                {
                    label: 'Goal Target',
                    data: scenarios.goalPath,
                    borderColor: '#FF3B30',
                    backgroundColor: 'rgba(255, 59, 48, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    borderDash: [8, 4]
                },
                {
                    label: `Advice-Based Growth (${(scenarios.growthProjections.rate * 100).toFixed(1)}% annual)`,
                    data: scenarios.adviceBasedGrowth,
                    borderColor: '#34C759',
                    backgroundColor: 'rgba(52, 199, 129, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Your Financial Journey: ${scenarios.goalAmount ? formatCurrency(scenarios.goalAmount) : 'Goal'} in ${timeframe} Years`,
                    font: {
                        size: 18,
                        weight: 'bold'
                    },
                    padding: 20
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Years',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Portfolio Value ($)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        },
                        font: {
                            size: 12
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            elements: {
                point: {
                    radius: 3,
                    hoverRadius: 8
                }
            }
        }
    });
    
    console.log('Chart created successfully');
}

function calculateGrowthScenarios(timeframe, currentSavings, monthlyIncome, monthlyExpenses) {
    const labels = [];
    const currentPath = [];
    const goalPath = [];
    const adviceBasedGrowth = [];
    
    // Monthly savings (income - expenses)
    const monthlySavings = Math.max(0, monthlyIncome - monthlyExpenses);
    
    // Calculate goal amount based on financial goal and timeframe
    const goalAmount = calculateGoalAmount(timeframe, currentSavings, monthlyIncome, monthlyExpenses);
    
    // Extract growth projections from LLM advice
    const growthProjections = extractGrowthProjectionsFromAdvice();
    
    // Use extracted monthly investment amount or fallback to calculated savings
    const effectiveMonthlyInvestment = growthProjections.monthlyInvestment > 0 ? 
        growthProjections.monthlyInvestment : monthlySavings * 0.6; // Use 60% of savings if no specific amount
    
    // Use extracted target amount if available, otherwise use calculated goal
    const effectiveGoalAmount = growthProjections.avgTargetAmount > 0 ? 
        growthProjections.avgTargetAmount : goalAmount;
    
    for (let year = 0; year <= timeframe; year++) {
        labels.push(`Year ${year}`);
        
        // Current path: what they'll have if they just save without investing
        const currentValue = currentSavings + (monthlySavings * 12 * year);
        currentPath.push(Math.round(currentValue));
        
        // Goal path: straight line to their target
        const goalProgress = currentSavings + ((effectiveGoalAmount - currentSavings) / timeframe) * year;
        goalPath.push(Math.round(goalProgress));
        
        // Advice-based growth: use actual LLM projections with extracted investment amounts
        const growthRate = growthProjections.rate || 0.07; // Default to 7% if no advice
        const adviceValue = calculateCompoundGrowth(currentSavings, effectiveMonthlyInvestment, growthRate, year);
        adviceBasedGrowth.push(Math.round(adviceValue));
    }
    
    return { 
        labels, 
        currentPath, 
        goalPath, 
        adviceBasedGrowth,
        goalAmount: effectiveGoalAmount,
        growthProjections,
        effectiveMonthlyInvestment: Math.round(effectiveMonthlyInvestment)
    };
}

function calculateGoalAmount(timeframe, currentSavings, monthlyIncome, monthlyExpenses) {
    // Calculate monthly savings
    const monthlySavings = Math.max(0, monthlyIncome - monthlyExpenses);
    const annualSavings = monthlySavings * 12;
    
    // Get financial goal from the page (we'll need to add this to the HTML)
    const financialGoal = getFinancialGoalFromPage();
    
    // Calculate target based on goal type
    let targetAmount = 0;
    
    switch (financialGoal) {
        case 'Buy a house':
            targetAmount = 500000; // Average house price, could be made configurable
            break;
        case 'Retire early':
            targetAmount = monthlyExpenses * 12 * 25; // 25x annual expenses (4% rule)
            break;
        case 'Build an emergency fund':
            targetAmount = monthlyExpenses * 6; // 6 months of expenses
            break;
        case 'Save for education':
            targetAmount = 100000; // College fund example
            break;
        case 'Start a business':
            targetAmount = 50000; // Business startup fund
            break;
        default:
            // Generic goal: aim for 10x current savings or 20x annual savings
            targetAmount = Math.max(currentSavings * 10, annualSavings * 20);
    }
    
    // Ensure target is achievable within timeframe
    const maxAchievable = currentSavings + (annualSavings * timeframe * 1.1); // 10% buffer
    return Math.min(targetAmount, maxAchievable);
}

function extractGrowthProjectionsFromAdvice() {
    // Look for growth projections in the LLM advice on the page
    const adviceElements = document.querySelectorAll('.advice-section');
    let bestGrowthRate = 0.07; // Default to 7%
    let bestGrowthText = '';
    let monthlyInvestmentAmount = 0;
    let targetAmounts = [];
    
    adviceElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        
        // Look for percentage mentions
        const percentageMatch = text.match(/(\d+(?:\.\d+)?)\s*%/);
        if (percentageMatch) {
            const rate = parseFloat(percentageMatch[1]) / 100;
            if (rate > bestGrowthRate && rate <= 0.15) { // Cap at 15% for realism
                bestGrowthRate = rate;
                bestGrowthText = text;
            }
        }
        
        // Look for growth keywords
        if (text.includes('growth') || text.includes('return') || text.includes('annual')) {
            // Extract numbers that might be growth rates
            const numberMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:percent|%|annual|yearly)/);
            if (numberMatch) {
                const rate = parseFloat(numberMatch[1]) / 100;
                if (rate > bestGrowthRate && rate <= 0.15) {
                    bestGrowthRate = rate;
                    bestGrowthText = text;
                }
            }
        }
        
        // Extract monthly investment amounts (e.g., "Invest $500 monthly", "Contribute $300 monthly")
        const monthlyInvestmentMatch = text.match(/(?:invest|contribute|allocate|save)\s*\$\s*([\d,]+)\s*(?:monthly|per month|a month)/i);
        if (monthlyInvestmentMatch) {
            const amount = parseInt(monthlyInvestmentMatch[1].replace(/,/g, ''));
            if (amount > monthlyInvestmentAmount) {
                monthlyInvestmentAmount = amount;
            }
        }
        
        // Extract target amounts (e.g., "grow to $50,000", "target of $100,000")
        const targetAmountMatch = text.match(/(?:grow to|target of|approximately|about)\s*\$\s*([\d,]+)/i);
        if (targetAmountMatch) {
            const amount = parseInt(targetAmountMatch[1].replace(/,/g, ''));
            targetAmounts.push(amount);
        }
        
        // Look for dollar amounts in growth projections
        const growthAmountMatch = text.match(/(?:could grow to|potential growth to|expected to reach)\s*\$\s*([\d,]+)/i);
        if (growthAmountMatch) {
            const amount = parseInt(growthAmountMatch[1].replace(/,/g, ''));
            targetAmounts.push(amount);
        }
    });
    
    // Calculate average target amount if multiple found
    const avgTargetAmount = targetAmounts.length > 0 ? 
        targetAmounts.reduce((sum, amount) => sum + amount, 0) / targetAmounts.length : 0;
    
    return {
        rate: bestGrowthRate,
        text: bestGrowthText,
        source: 'LLM Advice',
        monthlyInvestment: monthlyInvestmentAmount,
        targetAmounts: targetAmounts,
        avgTargetAmount: Math.round(avgTargetAmount)
    };
}

function getFinancialGoalFromPage() {
    // Get financial goal from the hidden data
    const financialGoalElement = document.getElementById('financialGoalData');
    if (financialGoalElement) {
        return financialGoalElement.textContent.trim();
    }
    
    // Fallback to common goals
    return 'Build wealth';
}

function calculateCompoundGrowth(initial, monthlyContribution, annualRate, years) {
    const monthlyRate = annualRate / 12;
    const months = years * 12;
    
    // Future value of initial investment
    const futureValueInitial = initial * Math.pow(1 + monthlyRate, months);
    
    // Future value of monthly contributions
    const futureValueContributions = monthlyContribution * 
        ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate);
    
    return futureValueInitial + futureValueContributions;
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add copy to clipboard functionality for advice
function copyAdviceToClipboard(adviceText) {
    navigator.clipboard.writeText(adviceText).then(function() {
        // Show success message
        const toast = document.createElement('div');
        toast.className = 'toast-success';
        toast.textContent = 'Advice copied to clipboard!';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    });
}

// Add CSS animation for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

// Function to setup custom fields for dropdowns
function setupCustomFields(selectId, customFieldId) {
    const selectElement = document.getElementById(selectId);
    const customField = document.getElementById(customFieldId);
    
    if (selectElement && customField) {
        selectElement.addEventListener('change', function() {
            if (this.value === 'custom') {
                customField.style.display = 'block';
                customField.required = true;
            } else {
                customField.style.display = 'none';
                customField.required = false;
                customField.value = '';
            }
        });
    }
}

// Function to update chart insights
function updateChartInsights(timeframe, currentSavings, monthlyIncome, monthlyExpenses) {
    const monthlySavings = Math.max(0, monthlyIncome - monthlyExpenses);
    const emergencyFundTarget = monthlyExpenses * 6;
    const emergencyFundStatus = currentSavings >= emergencyFundTarget ? 
        `✅ Fully funded (${Math.round((currentSavings / emergencyFundTarget) * 100)}%)` : 
        `⚠️ ${Math.round((currentSavings / emergencyFundTarget) * 100)}% funded (need $${(emergencyFundTarget - currentSavings).toLocaleString()})`;
    
    // Get growth projections from advice
    const growthProjections = extractGrowthProjectionsFromAdvice();
    const effectiveMonthlyInvestment = growthProjections.monthlyInvestment > 0 ? 
        growthProjections.monthlyInvestment : monthlySavings * 0.6;
    const effectiveGoalAmount = growthProjections.avgTargetAmount > 0 ? 
        growthProjections.avgTargetAmount : calculateGoalAmount(timeframe, currentSavings, monthlyIncome, monthlyExpenses);
    
    document.getElementById('emergency-fund-status').textContent = emergencyFundStatus;
    document.getElementById('monthly-savings-amount').textContent = `$${monthlySavings.toLocaleString()}`;
    
    // Show investment amount from advice if available
    if (growthProjections.monthlyInvestment > 0) {
        document.getElementById('growth-potential').textContent = 
            `$${growthProjections.monthlyInvestment.toLocaleString()} monthly investment (from advice)`;
    } else {
        document.getElementById('growth-potential').textContent = 
            `${Math.round((effectiveMonthlyInvestment / monthlySavings) * 100)}% of savings for growth`;
    }
    
    // Update goal information with extracted amounts
    const goalInfo = document.getElementById('goal-info');
    if (goalInfo) {
        const financialGoal = getFinancialGoalFromPage();
        const progressPercentage = Math.round((currentSavings / effectiveGoalAmount) * 100);
        
        goalInfo.innerHTML = `
            <div class="insight-item">🎯 <strong>Financial Goal:</strong> ${financialGoal}</div>
            <div class="insight-item">💰 <strong>Target Amount:</strong> $${effectiveGoalAmount.toLocaleString()}</div>
            <div class="insight-item">📊 <strong>Progress:</strong> ${progressPercentage}% ($${currentSavings.toLocaleString()} of $${effectiveGoalAmount.toLocaleString()})</div>
            ${growthProjections.monthlyInvestment > 0 ? 
                `<div class="insight-item">💡 <strong>Monthly Investment:</strong> $${growthProjections.monthlyInvestment.toLocaleString()} (from advice)</div>` : 
                `<div class="insight-item">💡 <strong>Recommended Investment:</strong> $${Math.round(effectiveMonthlyInvestment).toLocaleString()} monthly</div>`
            }
        `;
    }
}

// Function to update advice source message
function updateAdviceSourceMessage() {
    const adviceSourceElement = document.getElementById('advice-source');
    const adviceStatusElement = document.getElementById('advice-status');
    const statusIconElement = document.getElementById('status-icon');
    const statusTextElement = document.getElementById('status-text');
    
    if (!adviceSourceElement) return;
    
    // Check if we're on the results page
    const adviceCards = document.querySelectorAll('.advice-card');
    if (adviceCards.length === 0) return;
    
    // Look for specific fallback advice patterns
    const firstAdvice = adviceCards[0];
    const recommendationText = firstAdvice.querySelector('h3')?.textContent || '';
    const explanationText = firstAdvice.querySelector('.advice-section p')?.textContent || '';
    
    // Check if this is fallback advice (these are the specific fallback recommendations)
    const isFallback = recommendationText.includes('Build Emergency Fund') || 
                       recommendationText.includes('Diversified Investment Portfolio') ||
                       recommendationText.includes('Retirement Planning') ||
                       explanationText.includes('Start by saving 3-6 months of expenses');
    
    if (isFallback) {
        adviceSourceElement.textContent = '📚 Professional financial guidance (AI temporarily unavailable)';
        adviceSourceElement.style.color = 'var(--warning-color)';
        
        // Update status indicator
        if (adviceStatusElement && statusIconElement && statusTextElement) {
            adviceStatusElement.style.display = 'block';
            adviceStatusElement.style.background = 'rgba(255, 149, 0, 0.1)';
            adviceStatusElement.style.border = '1px solid var(--warning-color)';
            statusIconElement.textContent = '⚠️';
            statusTextElement.textContent = 'Using professional fallback guidance - AI analysis unavailable';
        }
    } else {
        adviceSourceElement.textContent = '🤖 AI-generated personalized recommendations';
        adviceSourceElement.style.color = 'var(--success-color)';
        
        // Update status indicator
        if (adviceStatusElement && statusIconElement && statusTextElement) {
            adviceStatusElement.style.display = 'block';
            adviceStatusElement.style.background = 'rgba(52, 199, 129, 0.1)';
            adviceStatusElement.style.border = '1px solid var(--success-color)';
            statusIconElement.textContent = '✅';
            statusTextElement.textContent = 'AI analysis completed successfully';
        }
    }
}
