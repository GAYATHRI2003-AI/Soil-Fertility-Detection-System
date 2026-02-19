// ========== MAIN JAVASCRIPT ========== //

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
        });
    }
    
    // Close menu when link clicked
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navMenu.style.display = 'none';
        });
    });
});

// ========== FORM VALIDATION ========== //

function validateSoilForm() {
    const form = document.getElementById('analysisForm');
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[type="number"]');
    let isValid = true;
    
    inputs.forEach(input => {
        const value = parseFloat(input.value);
        if (isNaN(value) || value < 0) {
            input.style.borderColor = '#ff6b6b';
            isValid = false;
        } else {
            input.style.borderColor = '#e2e8f0';
        }
    });
    
    return isValid;
}

// ========== SMOOTH SCROLLING ========== //

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

// ========== API CALL HELPERS ========== //

async function callAPI(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API Error');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showError(error.message);
        return null;
    }
}

// ========== NOTIFICATION HELPERS ========== //

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        background: ${type === 'success' ? '#43e97b' : type === 'error' ? '#ff6b6b' : '#4facfe'};
        color: white;
        font-weight: 600;
        z-index: 9999;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ========== RESULT DISPLAY ========== //

function displayStatusBadge(status) {
    const statusConfig = {
        'OPTIMAL': { color: '#43e97b', background: 'rgba(67, 233, 123, 0.2)' },
        'HIGH': { color: '#7ed321', background: 'rgba(126, 211, 33, 0.2)' },
        'MODERATE': { color: '#ffc933', background: 'rgba(255, 201, 51, 0.2)' },
        'LOW': { color: '#ff9f43', background: 'rgba(255, 159, 67, 0.2)' },
        'INFERTILE': { color: '#ff6b6b', background: 'rgba(255, 107, 107, 0.2)' }
    };
    
    const config = statusConfig[status] || statusConfig['MODERATE'];
    return `<span class="status-badge" style="color: ${config.color}; background: ${config.background};">${status}</span>`;
}

// ========== SOIL ANALYSIS FORM HANDLER ========== //

if (document.getElementById('analysisForm')) {
    document.getElementById('analysisForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validateSoilForm()) {
            showError('Please enter valid values for all fields');
            return;
        }
        
        const formData = {
            nitrogen: parseFloat(document.getElementById('nitrogen').value),
            phosphorus: parseFloat(document.getElementById('phosphorus').value),
            potassium: parseFloat(document.getElementById('potassium').value),
            ph: parseFloat(document.getElementById('ph').value),
            ec: parseFloat(document.getElementById('ec').value),
            oc: parseFloat(document.getElementById('oc').value),
            sulfur: parseFloat(document.getElementById('sulfur').value),
            zinc: parseFloat(document.getElementById('zinc').value),
            iron: parseFloat(document.getElementById('iron').value),
            boron: parseFloat(document.getElementById('boron').value)
        };
        
        showNotification('Analyzing soil parameters...', 'info');
        
        const result = await callAPI('/api/analyze', 'POST', formData);
        
        if (result && result.success) {
            displayResults(result.data);
            document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
            showSuccess('Soil analysis complete!');
        }
    });
}

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    
    let recommendationsHTML = '';
    if (data.recommendations && Array.isArray(data.recommendations)) {
        recommendationsHTML = data.recommendations.map(rec => `
            <div class="recommendation-item">
                <h5>🌱 ${rec.name || 'Recommendation'}</h5>
                <p><strong>Rate:</strong> ${rec.rate || 'N/A'}</p>
                <p><strong>Impact:</strong> ${rec.impact || 'Improves soil fertility'}</p>
            </div>
        `).join('');
    }
    
    let parameterCardsHTML = '';
    const params = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'ec', 'oc', 'sulfur', 'zinc', 'iron', 'boron'];
    params.forEach(param => {
        if (data[param] !== undefined) {
            parameterCardsHTML += `
                <div class="result-card">
                    <h5>${param.toUpperCase()}</h5>
                    <p class="result-value">${data[param]}</p>
                </div>
            `;
        }
    });
    
    const statusHTML = displayStatusBadge(data.classification || 'MODERATE');
    
    resultsSection.innerHTML = `
        <div class="results-section">
            <div class="result-cards">
                <div class="main-result">
                    <div class="result-score">
                        <p style="margin: 0;">Fertility Status</p>
                        ${statusHTML}
                    </div>
                    <div class="result-score">
                        <p style="margin: 0; opacity: 0.9;">Final Score</p>
                        <h2>${data.final_score || 'N/A'}</h2>
                    </div>
                </div>
            </div>
            
            ${data.limiting_factor ? `
                <div class="result-card">
                    <h4>⚠️ Limiting Factor</h4>
                    <p><strong>${data.limiting_factor}</strong></p>
                    <small>This is the primary factor limiting soil fertility</small>
                </div>
            ` : ''}
            
            ${data.index_score ? `
                <div class="result-card">
                    <h4>📊 Index Score</h4>
                    <p class="result-value">${data.index_score}</p>
                    <small>Fertility potential without limiting factor</small>
                </div>
            ` : ''}
            
            <div class="recommendations-section">
                <h3>💡 Recommendations</h3>
                <div class="recommendations-list">
                    ${recommendationsHTML || '<p>Apply soil amendments based on limiting factor</p>'}
                </div>
            </div>
            
            <div class="results-section" style="background: #f5f7fa; margin-top: 2rem;">
                <h3>📈 Parameter Assessment</h3>
                <div class="result-cards">
                    ${parameterCardsHTML}
                </div>
            </div>
        </div>
    `;
}

// ========== KNOWLEDGE BASE QUERY ========== //

if (document.getElementById('knowledgeForm')) {
    document.getElementById('knowledgeForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const question = document.getElementById('knowledgeInput').value.trim();
        if (!question) {
            showError('Please enter a question');
            return;
        }
        
        showNotification('Searching knowledge base...', 'info');
        
        const result = await callAPI('/api/knowledge-query', 'POST', { question });
        
        if (result && result.success) {
            displayKnowledgeResult(result);
            document.getElementById('knowledgeResults').scrollIntoView({ behavior: 'smooth' });
        }
    });
    
    // Suggestion chips
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            document.getElementById('knowledgeInput').value = this.textContent;
            document.getElementById('knowledgeForm').dispatchEvent(new Event('submit'));
        });
    });
}

function displayKnowledgeResult(data) {
    const resultsDiv = document.getElementById('knowledgeResults');
    
    resultsDiv.innerHTML = `
        <div class="results-section">
            <h3>${data.title || 'Knowledge Base Result'}</h3>
            <div class="result-card">
                <p>${data.answer || 'No answer found'}</p>
            </div>
            <div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">
                ${data.confidence ? `
                    <div class="result-card">
                        <p style="margin: 0;"><strong>Confidence:</strong></p>
                        <p class="result-value">${data.confidence}%</p>
                    </div>
                ` : ''}
                ${data.source_count ? `
                    <div class="result-card">
                        <p style="margin: 0;"><strong>Sources:</strong></p>
                        <p class="result-value">${data.source_count}</p>
                    </div>
                ` : ''}
            </div>
            <button class="btn btn-primary" onclick="document.getElementById('knowledgeInput').value = ''; document.getElementById('knowledgeInput').focus();">
                <i class="fas fa-search"></i> Ask Another Question
            </button>
        </div>
    `;
}

// ========== CROP ADVISOR ========== //

let selectedSeason = null;

function selectSeason(season) {
    selectedSeason = season;
    
    // Update UI
    document.querySelectorAll('.season-card').forEach(card => {
        card.classList.remove('active');
    });
    event.target.closest('.season-card').classList.add('active');
    
    // Show region selector
    document.getElementById('regionSelector').style.display = 'flex';
}

async function getCropRecommendations() {
    const region = document.getElementById('regionSelect').value;
    
    if (!selectedSeason) {
        showError('Please select a season');
        return;
    }
    
    if (!region) {
        showError('Please select a region');
        return;
    }
    
    showNotification('Fetching crop recommendations...', 'info');
    
    const result = await callAPI('/api/crop-recommendations', 'POST', {
        season: selectedSeason,
        region: region
    });
    
    if (result && result.success) {
        displayCropRecommendations(result);
        document.getElementById('cropsSection').scrollIntoView({ behavior: 'smooth' });
    }
}

function displayCropRecommendations(data) {
    const cropsSection = document.getElementById('cropsSection');
    
    let cropsHTML = '';
    if (data.crops && Array.isArray(data.crops)) {
        cropsHTML = data.crops.map(crop => `
            <div class="crop-card">
                <div class="crop-icon">
                    <i class="fas fa-leaf"></i>
                </div>
                <h4>${crop}</h4>
                <div>
                    <span class="season-tag">${data.season}</span>
                    <span class="region-tag">${data.region}</span>
                </div>
            </div>
        `).join('');
    }
    
    cropsSection.innerHTML = `
        <div class="results-section">
            <h2>🌾 Recommended Crops</h2>
            <p>Best crops for <strong>${data.season}</strong> season in <strong>${data.region}</strong></p>
            <div class="crops-grid">
                ${cropsHTML}
            </div>
        </div>
    `;
}

// ========== DASHBOARD CHART INITIALIZATION ========== //

if (document.getElementById('fertilityChart')) {
    const ctx = document.getElementById('fertilityChart').getContext('2d');
    const fertilityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Optimal', 'High', 'Moderate', 'Low', 'Infertile'],
            datasets: [{
                data: [35, 20, 25, 15, 5],
                backgroundColor: [
                    '#43e97b',
                    '#7ed321',
                    '#ffc933',
                    '#ff9f43',
                    '#ff6b6b'
                ],
                borderColor: 'white',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

if (document.getElementById('limitingFactorsChart')) {
    const ctx = document.getElementById('limitingFactorsChart').getContext('2d');
    const limitingChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['pH', 'OC', 'EC', 'N', 'P'],
            datasets: [{
                label: 'Number of Deficient Fields',
                data: [35, 28, 22, 18, 15],
                backgroundColor: 'rgba(102, 126, 234, 0.7)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// ========== PAGE LOAD STATS ========== //

async function loadDashboardStats() {
    const result = await callAPI('/api/dashboard-stats', 'GET');
    
    if (result && result.success) {
        document.querySelectorAll('.stat-number').forEach((el, index) => {
            const stats = [result.total_analyses, result.optimal_fields, result.needs_attention, result.kb_documents];
            if (stats[index]) {
                el.textContent = stats[index];
            }
        });
    }
}

// Load stats when dashboard page loads
if (document.querySelector('.dashboard-container')) {
    loadDashboardStats();
}

// ========== ANIMATIONS ========== //

// Add CSS animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
    
    .btn:active {
        transform: scale(0.98);
    }
`;
document.head.appendChild(style);

// ========== UTILITY FUNCTIONS ========== //

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function calculatePercentage(value, max) {
    return Math.round((value / max) * 100);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    console.log('FertilityPro Application Initialized');
});
