import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, Minus, Activity, Box, DollarSign, Target, Zap, Info, BarChart2 } from 'lucide-react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [kpiData, setKpiData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [elasticityData, setElasticityData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Form state
  const [formData, setFormData] = useState({
    price: 75.0,
    cost: 50.0,
    discount_pct: 10.0,
    inventory_units: 150,
    competitor_price: 80.0,
    category: 1,
    region: 0,
    seasonality: 2,
    weather_condition: 1,
    month: 4,
    day_of_week: 2
  });

  // Fetch KPI data
  useEffect(() => {
    const fetchKPIs = async () => {
      try {
        const response = await fetch(`${API_URL}/kpi/dashboard`);
        const data = await response.json();
        setKpiData(data);
      } catch (error) {
        console.error('Error fetching KPIs:', error);
      }
    };

    fetchKPIs();
    const interval = setInterval(fetchKPIs, 30000); // 30s
    return () => clearInterval(interval);
  }, []);

  // Handle prediction
  const handlePredict = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error('Error making prediction:', error);
    }
    setLoading(false);
  };

  // Handle elasticity analysis
  const handleElasticity = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/experiment/elasticity?base_price=${formData.price}&price_range=0.3&steps=20`
      );
      const data = await response.json();
      setElasticityData(data);
    } catch (error) {
      console.error('Error fetching elasticity:', error);
    }
    setLoading(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value) || 0
    }));
  };

  // Chart Data Preparation
  const chartData = elasticityData ? elasticityData.data_points.prices.map((price, index) => ({
    price: price.toFixed(2),
    demand: Math.round(elasticityData.data_points.demands[index]),
    revenue: Math.round(elasticityData.data_points.revenues[index]),
  })) : [];

  const KPICard = ({ title, value, subtitle, trend, icon: Icon }) => (
    <div className="kpi-card glass-panel">
      <div className="kpi-icon"><Icon /></div>
      <div className="kpi-content">
        <h3>{title}</h3>
        <div className="kpi-value">{value}</div>
        <div className="kpi-subtitle">
          {subtitle}
          {trend && (
            <span className={`trend trend-${trend}`}>
              {trend === 'up' && <TrendingUp size={16} />}
              {trend === 'down' && <TrendingDown size={16} />}
              {trend === 'stable' && <Minus size={16} />}
            </span>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="App">
      <header className="header glass-panel">
        <div className="header-content">
          <h1>PriceOptima Dashboard</h1>
          <p>ML-Powered Dynamic Pricing System</p>
        </div>
        <div className="header-status">
          <span className="status-indicator"></span>
          System Active
        </div>
      </header>

      <nav className="nav-tabs">
        <button className={activeTab === 'dashboard' ? 'active' : ''} onClick={() => setActiveTab('dashboard')}>
          <Activity size={18} style={{marginRight: '6px', verticalAlign: 'middle'}}/> Dashboard
        </button>
        <button className={activeTab === 'predict' ? 'active' : ''} onClick={() => setActiveTab('predict')}>
          <Zap size={18} style={{marginRight: '6px', verticalAlign: 'middle'}}/> Predict & Optimize
        </button>
        <button className={activeTab === 'analytics' ? 'active' : ''} onClick={() => setActiveTab('analytics')}>
          <BarChart2 size={18} style={{marginRight: '6px', verticalAlign: 'middle'}}/> Deep Analytics
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && kpiData && (
          <div className="dashboard-view">
            <h2><Activity size={28} color="var(--primary)" /> Real-Time KPIs</h2>
            
            <div className="kpi-grid">
              <KPICard title="Total Revenue" value={`₹${(kpiData.revenue.total / 1e6).toFixed(2)}M`} subtitle={`Daily Avg: ₹${(kpiData.revenue.daily_avg / 1e3).toFixed(1)}K`} trend={kpiData.revenue.trend} icon={DollarSign} />
              <KPICard title="ML Revenue Lift" value={`+${kpiData.revenue.ml_lift}%`} subtitle="vs Static Pricing" trend="up" icon={TrendingUp} />
              <KPICard title="Total Units Sold" value={kpiData.demand.total_units.toLocaleString()} subtitle={`Daily Avg: ${kpiData.demand.daily_avg}`} trend={kpiData.demand.trend} icon={Box} />
              <KPICard title="Forecast Accuracy" value={`${kpiData.demand.forecast_accuracy}%`} subtitle="Model R² Score" trend={kpiData.demand.trend} icon={Target} />
            </div>

            <div className="dashboard-metrics-container">
              <div className="chart-container glass-panel">
                <h3>Revenue Trajectory (Simulated)</h3>
                <ResponsiveContainer width="100%" height="85%">
                  <AreaChart data={[
                    {day: 'Mon', revenue: 120000}, {day: 'Tue', revenue: 140000},
                    {day: 'Wed', revenue: 145000}, {day: 'Thu', revenue: 160000},
                    {day: 'Fri', revenue: 180000}, {day: 'Sat', revenue: 210000}, {day: 'Sun', revenue: 220000}
                  ]}>
                    <defs>
                      <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="day" stroke="var(--text-secondary)" />
                    <YAxis stroke="var(--text-secondary)" />
                    <Tooltip contentStyle={{backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'var(--border)'}} itemStyle={{color: 'var(--primary)'}} />
                    <Area type="monotone" dataKey="revenue" stroke="var(--primary)" fillOpacity={1} fill="url(#colorRev)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="metrics-section glass-panel">
                <h3>System Health</h3>
                <div className="metrics-grid">
                  <div className="metric-item">
                    <span className="metric-label">Model RMSE</span>
                    <span className="metric-value">{kpiData.performance.model_rmse}</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Inference Latency</span>
                    <span className="metric-value">{kpiData.performance.prediction_latency_ms} ms</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Optimal Pricing Adoption</span>
                    <span className="metric-value">{kpiData.pricing.optimal_prices_applied}%</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="timestamp">Last updated: {new Date(kpiData.timestamp).toLocaleString()}</div>
          </div>
        )}

        {activeTab === 'predict' && (
          <div className="predict-view">
            <h2><Target size={28} color="var(--primary)" /> Demand Prediction & Price Optimization</h2>
            
            <div className="form-grid">
              <div className="form-section glass-panel">
                <h3>Product Details</h3>
                <div className="form-group"><label>Base Price (₹)</label><input type="number" name="price" value={formData.price} onChange={handleInputChange} /></div>
                <div className="form-group"><label>Unit Cost (₹)</label><input type="number" name="cost" value={formData.cost} onChange={handleInputChange} /></div>
                <div className="form-group"><label>Discount (%)</label><input type="number" name="discount_pct" value={formData.discount_pct} onChange={handleInputChange} /></div>
                <div className="form-group"><label>Available Inventory</label><input type="number" name="inventory_units" value={formData.inventory_units} onChange={handleInputChange} /></div>
              </div>

              <div className="form-section glass-panel">
                <h3>Market Context</h3>
                <div className="form-group"><label>Competitor Price (₹)</label><input type="number" name="competitor_price" value={formData.competitor_price} onChange={handleInputChange} /></div>
                <div className="form-group">
                  <label>Category</label>
                  <select name="category" value={formData.category} onChange={handleInputChange}>
                    <option value="0">Electronics</option>
                    <option value="1">Fashion</option>
                    <option value="2">Home & Kitchen</option>
                    <option value="3">Sports</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Region Zone</label>
                  <select name="region" value={formData.region} onChange={handleInputChange}>
                    <option value="0">North</option><option value="1">South</option><option value="2">East</option><option value="3">West</option>
                  </select>
                </div>
              </div>

              <div className="form-section glass-panel">
                <h3>Environmental State</h3>
                <div className="form-group">
                  <label>Seasonality</label>
                  <select name="seasonality" value={formData.seasonality} onChange={handleInputChange}>
                    <option value="0">Spring</option><option value="1">Summer</option><option value="2">Autumn</option><option value="3">Winter</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Weather</label>
                  <select name="weather_condition" value={formData.weather_condition} onChange={handleInputChange}>
                    <option value="0">Sunny</option><option value="1">Rainy</option><option value="2">Cloudy</option>
                  </select>
                </div>
                <div className="form-group"><label>Month (1-12)</label><input type="number" name="month" value={formData.month} onChange={handleInputChange} /></div>
              </div>
            </div>

            <div className="button-group">
              <button className="btn btn-primary" onClick={handlePredict} disabled={loading}>{loading ? 'Processing...' : 'Generate Prediction'}</button>
              <button className="btn btn-secondary" onClick={handleElasticity} disabled={loading}>Run Elasticity Analysis</button>
            </div>

            {prediction && (
              <div className="prediction-result glass-panel">
                <h3>Prediction Synced</h3>
                <div className="result-grid">
                  <div className="result-card">
                    <div className="result-label">Predicted Demand</div>
                    <div className="result-value">{prediction.predicted_demand.toFixed(0)}</div>
                  </div>
                  <div className="result-card">
                    <div className="result-label">Expected Revenue</div>
                    <div className="result-value">₹{prediction.expected_revenue.toLocaleString()}</div>
                  </div>
                  <div className="result-card">
                    <div className="result-label">Profit Margin</div>
                    <div className="result-value">{prediction.profit_margin.toFixed(1)}%</div>
                  </div>
                  <div className="result-card" style={{borderColor: 'var(--primary)', boxShadow: '0 0 20px rgba(74,222,128,0.1)'}}>
                    <div className="result-label" style={{color: 'var(--primary)'}}>Recommended Price</div>
                    <div className="result-value">₹{prediction.recommended_price.toFixed(2)}</div>
                  </div>
                </div>
                <div className="confidence-interval">
                  <strong>Prediction Interval (95% bounds):</strong> 
                  <span className="highlight-val">{prediction.confidence_interval.lower.toFixed(0)}</span> to <span className="highlight-val">{prediction.confidence_interval.upper.toFixed(0)}</span> units
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'analytics' && elasticityData && (
          <div className="analytics-view">
            <h2><BarChart2 size={28} color="var(--primary)" /> Deep Analytics Engine</h2>
            <div className="analytics-grid">
              <div className="elasticity-section glass-panel">
                <h3>Price Elasticity Analysis</h3>
                <div className="elasticity-summary">
                  <div className="summary-card"><span>Yield Optimal Price</span><strong className="high">₹{elasticityData.analysis.optimal_price.toFixed(2)}</strong></div>
                  <div className="summary-card"><span>Max Target Revenue</span><strong>₹{elasticityData.analysis.max_revenue.toLocaleString()}</strong></div>
                  <div className="summary-card"><span>Average Elasticity</span><strong>{elasticityData.analysis.avg_elasticity.toFixed(3)}</strong></div>
                  <div className="summary-card"><span>Demand Sentiment</span><strong className={elasticityData.analysis.demand_sensitivity}>{elasticityData.analysis.demand_sensitivity.toUpperCase()}</strong></div>
                </div>
                
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="price" stroke="var(--text-secondary)" label={{ value: 'Simulated Price (₹)', position: 'insideBottom', offset: -5, fill: 'var(--text-secondary)' }} />
                      <YAxis yAxisId="left" stroke="#8b5cf6" />
                      <YAxis yAxisId="right" orientation="right" stroke="var(--primary)" />
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <Tooltip contentStyle={{backgroundColor: 'rgba(15, 23, 42, 0.95)', border: '1px solid var(--border)', borderRadius: '8px'}} />
                      <Area yAxisId="left" type="monotone" dataKey="revenue" stroke="#8b5cf6" fill="url(#colorRevenue)" name="Expected Revenue (₹)" />
                      <Line yAxisId="right" type="monotone" dataKey="demand" stroke="var(--primary)" strokeWidth={3} dot={{r: 4, fill: 'var(--primary)'}} name="Demand (Units)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
              
              <div className="info-section">
                <h3><Info size={24} /> Engine Metrics & Theory</h3>
                <ul>
                  <li><strong>Market Elasticity Sensitivity</strong> Measures reaction to variance in target pricing constraints.</li>
                  <li><strong>Elasticity ≥ 1.0</strong> High reaction volatility indicating demand shrinks aggressively upon price hikes.</li>
                  <li><strong>Elasticity &lt; 1.0</strong> Stable bounds. Optimal condition for applying markups.</li>
                  <li><strong>Nash Optimal Price</strong> Predicted price that yields maximum revenue given environmental factors.</li>
                </ul>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'analytics' && !elasticityData && (
          <div className="analytics-view glass-panel" style={{textAlign: 'center', padding: '4rem'}}>
            <BarChart2 size={64} style={{color: 'var(--text-secondary)', marginBottom: '1rem', opacity: 0.5}} />
            <h3 style={{color: 'var(--text-secondary)'}}>No Elasticity Data Found</h3>
            <p style={{color: 'var(--text-secondary)'}}>Go to the <b>Predict & Optimize</b> tab and run the <b>Elasticity Analysis</b> to populate this dashboard.</p>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>PriceOptima Engine v1.0 | Milestone 6 Deployment | Powered by XGBoost Core</p>
      </footer>
    </div>
  );
}

export default App;
