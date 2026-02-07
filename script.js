// Configuration de l'API
const API_BASE_URL = 'http://127.0.0.1:8000';

// Données des actions CAC40 avec leurs informations
const CAC40_STOCKS = {
    "Air Liquide": { symbol: "AI.PA", sector: "Industrie" },
    "Airbus": { symbol: "AIR.PA", sector: "Industrie" },
    "ArcelorMittal": { symbol: "MT.AS", sector: "Industrie" },
    "AXA": { symbol: "CS.PA", sector: "Assurance" },
    "BNP Paribas": { symbol: "BNP.PA", sector: "Banque" },
    "Bouygues": { symbol: "EN.PA", sector: "Construction" },
    "Capgemini": { symbol: "CAP.PA", sector: "Technologie" },
    "Carrefour": { symbol: "CA.PA", sector: "Distribution" },
    "Crédit Agricole": { symbol: "ACA.PA", sector: "Banque" },
    "Danone": { symbol: "BN.PA", sector: "Consommation" },
    "Dassault Systèmes": { symbol: "DSY.PA", sector: "Technologie" },
    "Engie": { symbol: "ENGI.PA", sector: "Énergie" },
    "EssilorLuxottica": { symbol: "EL.PA", sector: "Santé" },
    "Eurofins Scientific": { symbol: "ERF.PA", sector: "Santé" },
    "Hermès": { symbol: "RMS.PA", sector: "Luxe" },
    "Kering": { symbol: "KER.PA", sector: "Luxe" },
    "Legrand": { symbol: "LR.PA", sector: "Industrie" },
    "L'Oréal": { symbol: "OR.PA", sector: "Consommation" },
    "LVMH": { symbol: "MC.PA", sector: "Luxe" },
    "Michelin": { symbol: "ML.PA", sector: "Industrie" },
    "Orange": { symbol: "ORA.PA", sector: "Technologie" },
    "Pernod Ricard": { symbol: "RI.PA", sector: "Consommation" },
    "Renault": { symbol: "RNO.PA", sector: "Automobile" },
    "Safran": { symbol: "SAF.PA", sector: "Industrie" },
    "Saint-Gobain": { symbol: "SGO.PA", sector: "Industrie" },
    "Sanofi": { symbol: "SAN.PA", sector: "Santé" },
    "Schneider Electric": { symbol: "SU.PA", sector: "Industrie" },
    "Société Générale": { symbol: "GLE.PA", sector: "Banque" },
    "STMicroelectronics": { symbol: "STM.PA", sector: "Technologie" },
    "Teleperformance": { symbol: "TEP.PA", sector: "Services" },
    "Thales": { symbol: "HO.PA", sector: "Défense" },
    "TotalEnergies": { symbol: "TTE.PA", sector: "Énergie" },
    "Unibail-Rodamco-Westfield": { symbol: "URW.AS", sector: "Immobilier" },
    "Veolia": { symbol: "VIE.PA", sector: "Services" },
    "Vinci": { symbol: "DG.PA", sector: "Construction" },
    "Vivendi": { symbol: "VIV.PA", sector: "Médias" }
};

// Variables globales
let fakeData = {};
let filteredStocks = Object.keys(CAC40_STOCKS);
let allStocksData = {};
let priceChart = null;
let currentStockName = null;
let comparedStockName = null;

// Éléments DOM
const searchInput = document.getElementById('searchInput');
const sectorFilter = document.getElementById('sectorFilter');
const performanceFilter = document.getElementById('performanceFilter');
const historyDays = document.getElementById('historyDays');
const applyFiltersBtn = document.getElementById('applyFilters');
const loadingIndicator = document.getElementById('loadingIndicator');
const stocksGrid = document.getElementById('stocksGrid');
const stockModal = document.getElementById('stockModal');
const closeModalBtn = document.getElementById('closeModal');

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setDefaultDates();
});

function initializeApp() {
    loadFakeData();
    loadAllStocksData();
    populateSectorFilter();
}

function setupEventListeners() {
    searchInput.addEventListener('input', handleSearch);
    applyFiltersBtn.addEventListener('click', applyFilters);
    closeModalBtn.addEventListener('click', closeModal);
    
    // Recharger les données quand la période change
    historyDays.addEventListener('change', function() {
        loadAllStocksData();
    });
    
    // Event listeners pour le comparateur
    document.getElementById('compareStock').addEventListener('click', compareWithStock);
    document.getElementById('clearComparison').addEventListener('click', clearComparison);
    document.getElementById('comparatorSearchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            compareWithStock();
        }
    });
    
    // Fermer le modal en cliquant à l'extérieur
    stockModal.addEventListener('click', function(e) {
        if (e.target === stockModal) {
            closeModal();
        }
    });
}

function setDefaultDates() {
    // Plus besoin de définir des dates par défaut
    // Les dernières valeurs sont chargées automatiquement
}

async function loadFakeData() {
    try {
        const response = await fetch('fake_data.json');
        fakeData = await response.json();
    } catch (error) {
        console.error('Erreur lors du chargement des données fake:', error);
        // Données par défaut si le fichier n'est pas trouvé
        fakeData = generateDefaultFakeData();
    }
}

async function loadAllStocksData(periodDays = null) {
    showLoading();
    try {
        // Utiliser la période sélectionnée ou 2 jours par défaut
        const days = periodDays || historyDays.value;
        const response = await fetch(`${API_BASE_URL}/get_latest_cac40_prices?period_days=${days}`);
        
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        allStocksData = await response.json();
        console.log('Dernières valeurs CAC40 chargées:', allStocksData);
        
        // Afficher les stocks avec les vraies données
        displayStocks();
        
    } catch (error) {
        console.error('Erreur lors du chargement des dernières valeurs CAC40:', error);
        // Fallback sur l'affichage basique
        displayStocks();
    } finally {
        hideLoading();
    }
}

function generateDefaultFakeData() {
    const defaultData = {};
    Object.keys(CAC40_STOCKS).forEach(stock => {
        defaultData[stock] = {
            confidence: Math.floor(Math.random() * 40) + 60,
            confidence_description: "Analyse en cours...",
            current_price: Math.random() * 500 + 50,
            projected_price: 0,
            projection_change: Math.random() * 20 - 10,
            projection_description: "Projection basée sur l'analyse technique et fondamentale.",
            keywords: ["analyse", "technique", "fondamentale", "marché"],
            sector: CAC40_STOCKS[stock].sector,
            performance: Math.random() > 0.5 ? "positive" : "negative"
        };
        defaultData[stock].projected_price = defaultData[stock].current_price * (1 + defaultData[stock].projection_change / 100);
    });
    return defaultData;
}

function populateSectorFilter() {
    const sectors = [...new Set(Object.values(CAC40_STOCKS).map(stock => stock.sector))];
    sectors.forEach(sector => {
        const option = document.createElement('option');
        option.value = sector;
        option.textContent = sector;
        sectorFilter.appendChild(option);
    });
}

function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase();
    filteredStocks = Object.keys(CAC40_STOCKS).filter(stock => 
        stock.toLowerCase().includes(searchTerm) ||
        CAC40_STOCKS[stock].symbol.toLowerCase().includes(searchTerm)
    );
    applyFilters();
}

function applyFilters() {
    showLoading();
    
    setTimeout(() => {
        let filtered = [...filteredStocks];
        
        // Filtre par secteur
        const selectedSector = sectorFilter.value;
        if (selectedSector) {
            filtered = filtered.filter(stock => 
                CAC40_STOCKS[stock].sector === selectedSector
            );
        }
        
        // Filtre par performance (utilise les données calculées par l'API)
        const selectedPerformance = performanceFilter.value;
        if (selectedPerformance) {
            filtered = filtered.filter(stock => {
                // Utiliser la performance calculée par l'API (comparaison début vs fin de période)
                if (allStocksData.stocks && allStocksData.stocks[stock]) {
                    const stockData = allStocksData.stocks[stock];
                    const performance = stockData.price_change;
                    
                    if (performance !== undefined) {
                        if (selectedPerformance === 'positive') {
                            return performance > 0;
                        } else if (selectedPerformance === 'negative') {
                            return performance < 0;
                        } else if (selectedPerformance === 'stable') {
                            return Math.abs(performance) < 1; // Moins de 1% de variation
                        }
                    }
                }
                return true;
            });
        }
        
        displayStocks(filtered);
        hideLoading();
    }, 500);
}

async function displayStocks(stocksToShow = filteredStocks) {
    stocksGrid.innerHTML = '';
    
    // Afficher les cartes avec les données réelles si disponibles
    stocksToShow.forEach(stock => {
        const stockCard = createStockCard(stock);
        stocksGrid.appendChild(stockCard);
    });
}

function createStockCard(stockName) {
    const stock = CAC40_STOCKS[stockName];
    const fakeStockData = fakeData[stockName];
    const realStockData = allStocksData.stocks ? allStocksData.stocks[stockName] : null;
    
    const card = document.createElement('div');
    card.className = 'stock-card';
    card.onclick = () => openStockDetail(stockName);
    
    // Utiliser les données réelles si disponibles
    let currentPrice = '--';
    let change = 0;
    let changeClass = 'neutral';
    
    if (realStockData && realStockData.last_price) {
        currentPrice = realStockData.last_price.toFixed(2);
        
        // Utiliser la performance calculée par l'API (comparaison début vs fin de période)
        change = realStockData.price_change || 0;
        changeClass = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
    } else if (fakeStockData) {
        // Fallback sur les données fake
        currentPrice = fakeStockData.current_price.toFixed(2);
        change = fakeStockData.projection_change;
        changeClass = change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral';
    }
    
    card.innerHTML = `
        <div class="stock-header">
            <div class="stock-name">${stockName}</div>
            <div class="stock-symbol">${stock.symbol}</div>
        </div>
        <div class="stock-price">${currentPrice} €</div>
        <div class="stock-change ${changeClass}">
            <i class="fas fa-arrow-${change > 0 ? 'up' : 'down'}"></i>
            ${change.toFixed(2)}%
        </div>
        <div class="stock-sparkline">
            <canvas class="sparkline-chart" width="200" height="40"></canvas>
        </div>
        <div class="stock-info">
            <p><strong>Secteur:</strong> ${stock.sector}</p>
            ${fakeStockData ? `<p><strong>Confiance:</strong> ${fakeStockData.confidence}/100</p>` : ''}
        </div>
    `;
    
    // Créer la sparkline après l'ajout au DOM
    setTimeout(() => {
        createSparkline(card, stockName);
    }, 100);
    
    return card;
}

async function openStockDetail(stockName) {
    currentStockName = stockName;
    showLoading();
    
    try {
        // Charger l'historique détaillé (30 derniers jours)
        const historyData = await fetchStockHistory(stockName);
        
        // Préparer les données pour l'affichage
        const stockInfo = CAC40_STOCKS[stockName];
        const fakeInfo = fakeData[stockName] || {};
        const latestData = allStocksData.stocks ? allStocksData.stocks[stockName] : null;
        
        // Mettre à jour le modal avec les données d'historique
        updateModalContent(stockName, stockInfo, fakeInfo, historyData, latestData);
        updateComparisonDisplay();
        
        // Afficher le modal
        stockModal.classList.remove('hidden');
        
    } catch (error) {
        console.error('Erreur lors du chargement des détails:', error);
        alert('Erreur lors du chargement des données de l\'action');
    } finally {
        hideLoading();
    }
}

async function fetchStockHistory(stockName, days = null) {
    try {
        // Utiliser la valeur du select si pas de paramètre
        const daysToFetch = days || historyDays.value;
        
        const response = await fetch(
            `${API_BASE_URL}/get_stock_history?stock=${encodeURIComponent(stockName)}&days=${daysToFetch}`
        );
        
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        // Récupérer directement le JSON depuis l'API
        const data = await response.json();
        
        return data;
        
    } catch (error) {
        console.error('Erreur API:', error);
        throw error; // Propager l'erreur pour la gestion en amont
    }
}

// Fonction de fallback pour compatibilité (plus utilisée)
async function fetchStockData(stockName) {
    // Cette fonction n'est plus utilisée avec la nouvelle architecture
    // Elle est gardée pour compatibilité
    return await fetchStockHistory(stockName);
}


function updateModalContent(stockName, stockInfo, fakeInfo, historyData, latestData) {
    // Titre
    document.getElementById('modalTitle').textContent = `${stockName} (${stockInfo.symbol})`;
    
    // Indice de confiance (toujours fake pour l'instant)
    // Mettre à jour l'indice de corrélation
    const correlation = fakeInfo.correlation || 0.75;
    document.getElementById('correlationScore').innerHTML = `
        <span class="score">${correlation.toFixed(2)}</span>
        <span class="label">/ 1.0</span>
    `;
    
    let correlationDescription = '';
    if (correlation > 0.8) {
        correlationDescription = 'Forte corrélation avec les indicateurs du marché. Données très fiables.';
    } else if (correlation > 0.6) {
        correlationDescription = 'Corrélation modérée. Données généralement fiables.';
    } else if (correlation > 0.4) {
        correlationDescription = 'Faible corrélation. Prudence recommandée dans l\'analyse.';
    } else {
        correlationDescription = 'Très faible corrélation. Données peu fiables.';
    }
    document.getElementById('correlationDescription').textContent = correlationDescription;
    
    // Projection avec données réelles si disponibles
    let currentPrice = fakeInfo.current_price || 100;
    let projectedPrice = fakeInfo.projected_price || currentPrice * 1.05;
    let change = fakeInfo.projection_change || 5;
    
    // Utiliser les données réelles pour le prix actuel et la projection
    if (latestData && latestData.last_price) {
        currentPrice = latestData.last_price;
        change = latestData.price_change || 0;
        
        // Calculer la projection basée sur l'historique si disponible
        if (historyData && historyData.open_prices && historyData.open_prices.length > 1) {
            const firstPrice = historyData.open_prices[0].open_price;
            const lastPrice = historyData.open_prices[historyData.open_prices.length - 1].open_price;
            const totalChange = ((lastPrice - firstPrice) / firstPrice) * 100;
            const dailyAverageChange = totalChange / historyData.open_prices.length;
            
            // Projection basée sur la tendance réelle
            projectedPrice = currentPrice * (1 + dailyAverageChange / 100 * 30); // 30 jours de projection
            change = ((projectedPrice - currentPrice) / currentPrice) * 100;
        } else {
            // Utiliser le changement quotidien pour la projection
            projectedPrice = currentPrice * (1 + change / 100 * 30);
        }
    } else if (historyData && historyData.open_prices && historyData.open_prices.length > 0) {
        // Fallback sur l'historique si pas de données latest
        const latestPrice = historyData.open_prices[historyData.open_prices.length - 1];
        currentPrice = latestPrice.open_price;
        
        if (historyData.open_prices.length > 1) {
            const firstPrice = historyData.open_prices[0].open_price;
            const totalChange = ((latestPrice.open_price - firstPrice) / firstPrice) * 100;
            const dailyAverageChange = totalChange / historyData.open_prices.length;
            
            projectedPrice = currentPrice * (1 + dailyAverageChange / 100 * 30);
            change = ((projectedPrice - currentPrice) / currentPrice) * 100;
        }
    }
    
    document.getElementById('currentPrice').textContent = `${currentPrice.toFixed(2)} €`;
    document.getElementById('projectedPrice').textContent = `${projectedPrice.toFixed(2)} €`;
    
    const changeElement = document.getElementById('projectionChange');
    const changeValueElement = changeElement.querySelector('.change-value');
    if (changeValueElement) {
        changeValueElement.textContent = `${change > 0 ? '+' : ''}${change.toFixed(1)}%`;
        changeValueElement.className = `change-value ${change > 0 ? 'positive' : 'negative'}`;
    } else {
        // Fallback si la structure n'est pas encore mise à jour
        changeElement.textContent = `${change > 0 ? '+' : ''}${change.toFixed(2)}%`;
        changeElement.className = `projection-change ${change > 0 ? 'positive' : 'negative'}`;
    }
    
    // La description de projection est maintenant dans l'HTML avec l'explication détaillée
    
    // Mots-clés (toujours fake pour l'instant)
    const keywordsContainer = document.getElementById('keywordsList');
    keywordsContainer.innerHTML = '';
    
    const keywords = fakeInfo.keywords || ['analyse', 'technique', 'fondamentale'];
    keywords.forEach(keyword => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.textContent = keyword;
        keywordsContainer.appendChild(tag);
    });
    
    // Graphique avec données d'historique
    updateChart(historyData.open_prices);
    
    // Mettre à jour l'indicateur de sentiment
    updateSentimentIndicator(historyData.open_prices);
}

function updateChart(priceData) {
    const canvas = document.getElementById('priceChart');
    const ctx = canvas.getContext('2d');
    
    // Détruire le graphique précédent s'il existe
    if (priceChart) {
        priceChart.destroy();
    }
    
    if (priceData && priceData.length > 0) {
        // Préparer les données pour Chart.js
        const labels = priceData.map(item => {
            const date = new Date(item.date);
            return date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' });
        });
        
        const prices = priceData.map(item => item.open_price);
        
        // Générer des données de sentiment fictives (entre -1 et 1)
        const sentiments = generateSentimentData(priceData.length);
        
        // Générer des prédictions fictives (7 jours dans le futur)
        const predictionData = generatePredictionData(prices);
        const predictionLabels = generatePredictionLabels(labels, 7);
        
        // Couleur du graphique basée sur la tendance
        const firstPrice = prices[0];
        const lastPrice = prices[prices.length - 1];
        const isPositive = lastPrice >= firstPrice;
        const priceColor = isPositive ? '#27ae60' : '#e74c3c';
        
        // Calculer le prix moyen pour l'échelle du sentiment
        const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
        const sentimentScale = avgPrice * 0.3; // Échelle pour le sentiment
        
        priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [...labels, ...predictionLabels],
                datasets: [
                    {
                        label: 'Prix d\'ouverture (€)',
                        data: [...prices, ...new Array(7).fill(null)], // Prix historiques + prédictions vides
                        borderColor: priceColor,
                        backgroundColor: priceColor + '20',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4,
                        pointBackgroundColor: priceColor,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Prédiction (€)',
                        data: [...new Array(prices.length).fill(null), ...predictionData], // Historique vide + prédictions
                        borderColor: '#ff6b6b',
                        backgroundColor: '#ff6b6b' + '20',
                        borderWidth: 3,
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        pointBackgroundColor: '#ff6b6b',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 5,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Sentiment',
                        data: sentiments.map(s => avgPrice + (s * sentimentScale)),
                        borderColor: '#4ecdc4',
                        backgroundColor: '#4ecdc4' + '20',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.3,
                        pointBackgroundColor: '#4ecdc4',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 1,
                        pointRadius: 2,
                        pointHoverRadius: 4,
                        yAxisID: 'y',
                        hidden: false // Visible par défaut
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
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
                        callbacks: {
                            label: function(context) {
                                const datasetLabel = context.dataset.label;
                                const value = context.parsed.y;
                                
                                if (datasetLabel === 'Sentiment') {
                                    const sentimentValue = sentiments[context.dataIndex];
                                    return `${datasetLabel}: ${sentimentValue.toFixed(2)}`;
                                } else {
                                    return `${datasetLabel}: ${value.toFixed(2)} €`;
                                }
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxTicksLimit: 10,
                            callback: function(value, index) {
                                // Afficher seulement certaines dates pour éviter l'encombrement
                                return index % Math.ceil(labels.length / 8) === 0 ? this.getLabelForValue(value) : '';
                            }
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        grid: {
                            color: '#f3f4f6',
                            drawBorder: false
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(2) + ' €';
                            }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: false, // Masqué par défaut
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(2);
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                elements: {
                    point: {
                        hoverRadius: 8
                    }
                }
            }
        });
    } else {
        // Afficher un message d'erreur si pas de données
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#7f8c8d';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée disponible', canvas.width / 2, canvas.height / 2);
    }
}

function generateSentimentData(length) {
    // Générer des données de sentiment réalistes basées sur des patterns
    const sentiments = [];
    let currentSentiment = (Math.random() - 0.5) * 0.4; // Entre -0.2 et 0.2
    
    for (let i = 0; i < length; i++) {
        // Ajouter de la volatilité au sentiment
        const volatility = (Math.random() - 0.5) * 0.3;
        currentSentiment += volatility;
        
        // Limiter entre -1 et 1
        currentSentiment = Math.max(-1, Math.min(1, currentSentiment));
        
        // Ajouter une tendance basée sur la position dans le temps
        const trend = Math.sin(i / length * Math.PI * 2) * 0.2;
        currentSentiment += trend;
        
        sentiments.push(Math.max(-1, Math.min(1, currentSentiment)));
    }
    
    return sentiments;
}

function generatePredictionData(historicalPrices) {
    // Générer des prédictions basées sur la tendance historique
    const predictions = [];
    const lastPrice = historicalPrices[historicalPrices.length - 1];
    const secondLastPrice = historicalPrices[historicalPrices.length - 2];
    
    // Calculer la tendance
    const trend = (lastPrice - secondLastPrice) / secondLastPrice;
    
    // Générer 7 prédictions
    for (let i = 1; i <= 7; i++) {
        // Appliquer la tendance avec de la volatilité
        const volatility = (Math.random() - 0.5) * 0.02; // ±1% de volatilité
        const predictedPrice = lastPrice * Math.pow(1 + trend + volatility, i);
        
        predictions.push(predictedPrice);
    }
    
    return predictions;
}

function generatePredictionLabels(historicalLabels, predictionDays) {
    const predictionLabels = [];
    const lastDate = new Date(historicalLabels[historicalLabels.length - 1]);
    
    for (let i = 1; i <= predictionDays; i++) {
        const futureDate = new Date(lastDate);
        futureDate.setDate(futureDate.getDate() + i);
        
        // Skip weekends
        while (futureDate.getDay() === 0 || futureDate.getDay() === 6) {
            futureDate.setDate(futureDate.getDate() + 1);
        }
        
        predictionLabels.push(futureDate.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }));
    }
    
    return predictionLabels;
}

function updateSentimentIndicator(priceData) {
    if (!priceData || priceData.length === 0) return;
    
    // Générer les mêmes données de sentiment que pour le graphique
    const sentiments = generateSentimentData(priceData.length);
    
    // Calculer le sentiment moyen
    const avgSentiment = sentiments.reduce((a, b) => a + b, 0) / sentiments.length;
    
    // Mettre à jour seulement la barre de sentiment
    const sentimentFill = document.getElementById('sentimentFill');
    const percentage = ((avgSentiment + 1) / 2) * 100; // Convertir de [-1,1] à [0,100]
    sentimentFill.style.width = `${percentage}%`;
    
    // Changer la couleur selon le sentiment
    if (avgSentiment > 0.2) {
        sentimentFill.style.background = 'linear-gradient(90deg, #10b981 0%, #059669 100%)';
    } else if (avgSentiment < -0.2) {
        sentimentFill.style.background = 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)';
    } else {
        sentimentFill.style.background = 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)';
    }
}

function createSparkline(card, stockName) {
    const canvas = card.querySelector('.sparkline-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Générer des données de prix fictives pour la sparkline (mini tendance)
    const dataPoints = 20;
    const prices = generateSparklineData(dataPoints, stockName);
    
    // Calculer les dimensions du graphique
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice || 1;
    
    // Dessiner la sparkline
    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = prices[prices.length - 1] > prices[0] ? '#059669' : '#dc2626';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    prices.forEach((price, index) => {
        const x = (index / (dataPoints - 1)) * width;
        const y = height - ((price - minPrice) / priceRange) * height;
        
        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    // Ajouter un point pour la dernière valeur
    const lastX = width;
    const lastY = height - ((prices[prices.length - 1] - minPrice) / priceRange) * height;
    ctx.fillStyle = ctx.strokeStyle;
    ctx.beginPath();
    ctx.arc(lastX, lastY, 2, 0, 2 * Math.PI);
    ctx.fill();
}

function generateSparklineData(points, stockName) {
    // Générer des données réalistes basées sur le nom de l'action
    const basePrice = 50 + (stockName.length * 5); // Prix de base variable
    const prices = [basePrice];
    
    for (let i = 1; i < points; i++) {
        const volatility = (Math.random() - 0.5) * 4; // Volatilité de ±2%
        const trend = Math.sin(i / points * Math.PI * 2) * 2; // Tendance cyclique
        const newPrice = prices[i - 1] * (1 + (volatility + trend) / 100);
        prices.push(Math.max(newPrice, basePrice * 0.8)); // Prix minimum
    }
    
    return prices;
}

async function compareWithStock() {
    const searchInput = document.getElementById('comparatorSearchInput');
    const stockToCompare = searchInput.value.trim();
    
    if (!stockToCompare || !currentStockName) {
        alert('Veuillez entrer le nom d\'une action à comparer.');
        return;
    }
    
    // Vérifier que l'action existe
    if (!CAC40_STOCKS[stockToCompare]) {
        alert(`Action "${stockToCompare}" non trouvée. Veuillez vérifier le nom.`);
        return;
    }
    
    // Vérifier qu'on ne compare pas avec soi-même
    if (stockToCompare === currentStockName) {
        alert('Vous ne pouvez pas comparer une action avec elle-même.');
        return;
    }
    
    showLoading();
    try {
        comparedStockName = stockToCompare;
        
        // Charger les données des deux actions
        const [currentData, comparedData] = await Promise.all([
            fetchStockHistory(currentStockName),
            fetchStockHistory(stockToCompare)
        ]);
        
        // Mettre à jour l'affichage et le graphique
        updateComparisonDisplay();
        updateChartWithComparison(currentData.open_prices, comparedData.open_prices);
        
        // Vider le champ de recherche
        searchInput.value = '';
        
    } catch (error) {
        console.error('Erreur lors de la comparaison:', error);
        alert('Erreur lors du chargement des données de comparaison.');
    } finally {
        hideLoading();
    }
}

function clearComparison() {
    comparedStockName = null;
    updateComparisonDisplay();
    
    // Recharger le graphique normal
    if (currentStockName) {
        fetchStockHistory(currentStockName).then(data => {
            updateChart(data.open_prices);
        });
    }
}

function updateComparisonDisplay() {
    const clearBtn = document.getElementById('clearComparison');
    
    if (comparedStockName) {
        clearBtn.style.display = 'flex';
        // Mettre à jour le titre du graphique pour indiquer la comparaison
        document.querySelector('.chart-header h3').textContent = 
            `Analyse des prix - ${currentStockName} vs ${comparedStockName}`;
    } else {
        clearBtn.style.display = 'none';
        document.querySelector('.chart-header h3').textContent = 'Analyse des prix';
    }
}

function updateChartWithComparison(currentPrices, comparedPrices) {
    const canvas = document.getElementById('priceChart');
    const ctx = canvas.getContext('2d');
    
    // Détruire le graphique précédent
    if (priceChart) {
        priceChart.destroy();
    }
    
    if (!currentPrices || !comparedPrices || currentPrices.length === 0 || comparedPrices.length === 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#7f8c8d';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('Aucune donnée disponible', canvas.width / 2, canvas.height / 2);
        return;
    }
    
    // Préparer les données pour les deux actions
    const currentData = currentPrices.map(item => item.open_price);
    const comparedData = comparedPrices.map(item => item.open_price);
    
    // Utiliser les labels de la première action (même période)
    const labels = currentPrices.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' });
    });
    
    // Couleurs distinctes pour chaque action
    const currentColor = '#3b82f6'; // Bleu pour l'action principale
    const comparedColor = '#ef4444'; // Rouge pour l'action comparée
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: currentStockName,
                    data: currentData,
                    borderColor: currentColor,
                    backgroundColor: currentColor + '20',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5
                },
                {
                    label: comparedStockName,
                    data: comparedData,
                    borderColor: comparedColor,
                    backgroundColor: comparedColor + '20',
                    borderWidth: 3,
                    borderDash: [5, 5], // Ligne pointillée pour différencier
                    fill: false,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 10
                    }
                },
                y: {
                    display: true,
                    grid: {
                        color: '#f3f4f6',
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(2) + ' €';
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

function closeModal() {
    stockModal.classList.add('hidden');
    // Réinitialiser la comparaison quand on ferme le modal
    comparedStockName = null;
    currentStockName = null;
    document.getElementById('comparatorSearchInput').value = '';
}

function showLoading() {
    loadingIndicator.classList.remove('hidden');
}

function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

// Gestion des erreurs globales
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
});

// Export pour utilisation dans d'autres scripts si nécessaire
window.CAC40Dashboard = {
    CAC40_STOCKS,
    openStockDetail,
    applyFilters
};
