import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Calculator, DollarSign, TrendingUp, Package, AlertCircle, Cpu } from 'lucide-react';

function App() {
  const [formData, setFormData] = useState({
    product_id: 'P123',
    price: 100,
    cost: 70,
    inventory_level: 50,
    demand_forecast: 40,
    competitor_pricing: 95,
    visitors: 200,
    date: new Date().toISOString().split('T')[0]
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: ['product_id', 'date'].includes(name) ? value : Number(value)
    });
  };

  const handleOptimize = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // In a real deployed environment, replace with full backend URL if necessary
      const response = await axios.post('http://localhost:8000/predict-price', formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to connect to the Optimization Engine.');
    } finally {
      setLoading(false);
    }
  };

  const chartData = result ? [
    {
      name: 'Current Strategy',
      Price: formData.price,
      Demand: formData.demand_forecast,
      Revenue: formData.price * formData.demand_forecast
    },
    {
      name: 'AI Optimized',
      Price: result.optimal_price,
      Demand: result.predicted_demand,
      Revenue: result.expected_revenue
    }
  ] : [];

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1>PriceOptima AI</h1>
        <p>Enterprise Dynamic Pricing & Yield Management</p>
      </header>

      <div className="main-grid">
        <div className="glass-card input-section">
          <h2 className="card-title">
            <Calculator size={24} color="var(--primary)" />
            Scenario Parameters
          </h2>
          
          <form onSubmit={handleOptimize}>
            <div className="form-group">
              <label>Product ID</label>
              <input type="text" name="product_id" value={formData.product_id} onChange={handleInputChange} className="form-control" />
            </div>
            
            <div className="form-group">
              <label>Current Retail Price ($)</label>
              <input type="number" name="price" value={formData.price} onChange={handleInputChange} className="form-control" step="0.01" />
            </div>

            <div className="form-group">
              <label>Unit Cost ($)</label>
              <input type="number" name="cost" value={formData.cost} onChange={handleInputChange} className="form-control" step="0.01" />
            </div>

            <div className="form-group">
              <label>Inventory Level</label>
              <input type="number" name="inventory_level" value={formData.inventory_level} onChange={handleInputChange} className="form-control" />
            </div>

            <div className="form-group">
              <label>Demand Forecast (Units)</label>
              <input type="number" name="demand_forecast" value={formData.demand_forecast} onChange={handleInputChange} className="form-control" />
            </div>

            <div className="form-group">
              <label>Competitor Pricing ($)</label>
              <input type="number" name="competitor_pricing" value={formData.competitor_pricing} onChange={handleInputChange} className="form-control" step="0.01" />
            </div>

            <div className="form-group">
              <label>Expected Visitors</label>
              <input type="number" name="visitors" value={formData.visitors} onChange={handleInputChange} className="form-control" />
            </div>

            <div className="form-group">
              <label>Simulation Date</label>
              <input type="date" name="date" value={formData.date} onChange={handleInputChange} className="form-control" />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <Cpu className="loading-spinner" /> : <Cpu />}
              {loading ? 'Processing AI Models...' : 'Generate Optimal Price'}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: '1rem', color: '#ef4444', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={20} />
              {error}
            </div>
          )}
        </div>

        <div className="results-section">
          {result ? (
            <div className="glass-card">
              <h2 className="card-title">
                <TrendingUp size={24} color="var(--secondary)" />
                AI Recommendation
              </h2>

              <div className="results-grid">
                <div className="metric-card">
                  <div className="metric-title">Optimal Price</div>
                  <div className="metric-value highlight">${result.optimal_price.toFixed(2)}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-title">Predicted Demand</div>
                  <div className="metric-value">{result.predicted_demand}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-title">Expected Revenue</div>
                  <div className="metric-value highlight">${result.expected_revenue.toLocaleString()}</div>
                </div>
              </div>

              <div className="chart-container">
                <h3 style={{ color: 'var(--text-muted)', marginBottom: '1rem', textAlign: 'center' }}>Strategy Comparison: Revenue Impact</h3>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="name" stroke="#94a3b8" />
                    <YAxis yAxisId="left" orientation="left" stroke="#8b5cf6" />
                    <YAxis yAxisId="right" orientation="right" stroke="#10b981" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} />
                    <Legend />
                    <Bar yAxisId="left" dataKey="Revenue" fill="#8b5cf6" name="Total Revenue ($)" radius={[4, 4, 0, 0]} />
                    <Bar yAxisId="right" dataKey="Demand" fill="#10b981" name="Units Sold" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '400px', color: 'var(--text-muted)' }}>
              <Package size={64} style={{ marginBottom: '1rem', opacity: 0.5 }} />
              <h2>No Prediction Generated</h2>
              <p>Enter your scenario parameters and click Generate to see AI insights.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
