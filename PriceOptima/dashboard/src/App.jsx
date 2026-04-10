import { useState } from 'react';
import './index.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  
  // KPI Dashboard State
  const [kpis, setKpis] = useState({
    revenue: { value: '$24,500', trend: '+12.5%', isPositive: true },
    demand: { value: '845 units', trend: '+5.2%', isPositive: true },
    avgPrice: { value: '$89.50', trend: '-1.5%', isPositive: false }
  });

  // Form State
  const [formData, setFormData] = useState({
    inventory_level: 120,
    units_sold: 45,
    units_ordered: 50,
    demand_forecast: 48,
    discount: 5.0,
    holiday_promotion: 0,
    competitor_pricing: 85.0,
    visitors: 500,
    cost: 60.0,
    demand_ratio: 0.94,
    inventory_pressure: 0.38,
    stock_remaining: 75,
    conversion_rate: 0.09,
    traffic_intensity: 4.17,
    day_of_week: 3,
    month: 6,
    is_weekend: 0,
    category: "Electronics",
    region: "North",
    seasonality: "Summer",
    weather_condition: "Clear"
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    let parsedValue = value;
    
    // Parse numbers automatically layout based on type
    if (type === 'number') {
      parsedValue = parseFloat(value);
    }

    setFormData(prev => ({
      ...prev,
      [name]: parsedValue
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        throw new Error('API Request Failed');
      }
      
      const data = await response.json();
      setResult(data);
      
      // Update KPIs based on prediction to make the dashboard dynamic
      const predictedRev = data.predicted_price * 50; // Mock 50 units avg projected
      setKpis({
        revenue: { 
          value: `$${predictedRev.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits:0})}`, 
          trend: '+15.4%', 
          isPositive: true 
        },
        demand: { value: '920 units', trend: '+8.8%', isPositive: true },
        avgPrice: { value: `$${data.predicted_price}`, trend: '+2.1%', isPositive: true }
      });
      
    } catch (error) {
      console.error("Error predicting price:", error);
      alert("Failed to connect to AI PriceOptima API. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1 className="title">AI PriceOptima</h1>
        <p className="subtitle">Dynamic Pricing Intelligence Platform</p>
      </header>

      {/* KPI Dashboard Grid */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-label">Total Revenue</div>
          <div className="kpi-value">{kpis.revenue.value}</div>
          <div className={`kpi-trend ${kpis.revenue.isPositive ? 'positive' : 'neutral'}`}>
            {kpis.revenue.isPositive ? '↗' : '↘'} {kpis.revenue.trend} vs last month
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Projected Demand</div>
          <div className="kpi-value">{kpis.demand.value}</div>
          <div className={`kpi-trend ${kpis.demand.isPositive ? 'positive' : 'neutral'}`}>
            {kpis.demand.isPositive ? '↗' : '↘'} {kpis.demand.trend} vs last month
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Average Price</div>
          <div className="kpi-value">{kpis.avgPrice.value}</div>
          <div className={`kpi-trend ${kpis.avgPrice.isPositive ? 'positive' : 'neutral'}`}>
            {kpis.avgPrice.isPositive ? '↗' : '↘'} {kpis.avgPrice.trend} vs last month
          </div>
        </div>
      </div>

      <div className="main-grid">
        {/* Prediction Form */}
        <div className="form-container">
          <h2 className="form-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            Market Input Parameters
          </h2>
          <form className="form-grid" onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label">Competitor Price ($)</label>
              <input type="number" step="0.01" name="competitor_pricing" value={formData.competitor_pricing} onChange={handleChange} className="input-field" required />
            </div>
            <div className="input-group">
              <label className="input-label">Unit Cost ($)</label>
              <input type="number" step="0.01" name="cost" value={formData.cost} onChange={handleChange} className="input-field" required />
            </div>
            <div className="input-group">
              <label className="input-label">Inventory Level</label>
              <input type="number" name="inventory_level" value={formData.inventory_level} onChange={handleChange} className="input-field" required />
            </div>
            <div className="input-group">
              <label className="input-label">Demand Forecast</label>
              <input type="number" name="demand_forecast" value={formData.demand_forecast} onChange={handleChange} className="input-field" required />
            </div>
            <div className="input-group">
              <label className="input-label">Visitors</label>
              <input type="number" name="visitors" value={formData.visitors} onChange={handleChange} className="input-field" required />
            </div>
            <div className="input-group">
              <label className="input-label">Discount (%)</label>
              <input type="number" step="0.1" name="discount" value={formData.discount} onChange={handleChange} className="input-field" required />
            </div>
            <div className="input-group">
              <label className="input-label">Category</label>
              <select name="category" value={formData.category} onChange={handleChange} className="input-field">
                <option value="Electronics">Electronics</option>
                <option value="Apparel">Apparel</option>
                <option value="Home & Garden">Home & Garden</option>
              </select>
            </div>
            <div className="input-group">
              <label className="input-label">Seasonality</label>
              <select name="seasonality" value={formData.seasonality} onChange={handleChange} className="input-field">
                <option value="Spring">Spring</option>
                <option value="Summer">Summer</option>
                <option value="Fall">Fall</option>
                <option value="Winter">Winter</option>
              </select>
            </div>
            
            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? <div className="loader"></div> : 'Optimize Price Intelligence'}
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div className="results-container">
          {result ? (
            <div className="result-card">
              <div className="optimal-price-circle">
                <div className="price-label">Optimal Target Price</div>
                <div className="price-value">${result.predicted_price.toFixed(2)}</div>
              </div>
              
              <div className="stats-grid">
                <div className="stat-box">
                  <div className="stat-label">Market Positioning</div>
                  <div className="stat-value premium">{result.pricing_position.split(' ')[0]}</div>
                </div>
                <div className="stat-box">
                  <div className="stat-label">Estimated Margin</div>
                  <div className="stat-value margin">{result.margin_percent}%</div>
                </div>
                <div className="stat-box">
                  <div className="stat-label">Competitor Price</div>
                  <div className="stat-value">${result.competitor_price.toFixed(2)}</div>
                </div>
                <div className="stat-box">
                  <div className="stat-label">AI Confidence (R²)</div>
                  <div className="stat-value">{result.confidence_r2.toFixed(3)}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="result-card" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div className="empty-state">
                <div className="empty-icon">✨</div>
                <h3>AI Waiting for Input</h3>
                <p>Adjust market parameters and click optimize to generate pricing intelligence.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
