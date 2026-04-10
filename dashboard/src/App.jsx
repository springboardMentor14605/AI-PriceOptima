import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { TrendingUp, Activity, DollarSign, Package, Calendar } from 'lucide-react';
import './index.css';

const API_BASE = 'http://localhost:8000';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip">
        <p className="label">{label}</p>
        {payload.map((entry, index) => (
          <p key={`item-${index}`} style={{ color: entry.color }}>
            {entry.name}: ${entry.value.toFixed(2)}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

function App() {
  const [kpiData, setKpiData] = useState(null);
  const [loadingKpi, setLoadingKpi] = useState(true);
  
  // Simulator State
  const [basePrice, setBasePrice] = useState(100);
  const [inventory, setInventory] = useState(150);
  const [dayOfWeek, setDayOfWeek] = useState(3);
  const [simResult, setSimResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  useEffect(() => {
    fetchKpis();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      runSimulation(basePrice, inventory, dayOfWeek);
    }, 100);
    return () => clearTimeout(timer);
  }, [basePrice, inventory, dayOfWeek]);

  const fetchKpis = async () => {
    try {
      setLoadingKpi(true);
      const res = await axios.get(`${API_BASE}/kpi`);
      setKpiData(res.data);
    } catch (err) {
      console.error("Error fetching KPIs", err);
    } finally {
      setLoadingKpi(false);
    }
  };

  const runSimulation = async (price, inv, day) => {
    try {
      setSimLoading(true);
      const res = await axios.post(`${API_BASE}/pricing/predict`, {
        price: Number(price),
        inventory: Number(inv),
        day_of_week: Number(day)
      });
      setSimResult(res.data);
    } catch (err) {
      console.error("Simulation error", err);
    } finally {
      setSimLoading(false);
    }
  };

  const handleSimulate = (e) => {
    e.preventDefault();
  };

  let displayRatio = 1;
  if (simResult && simResult.original_price > 0) {
    displayRatio = simResult.dynamic_price / simResult.original_price;
  }

  const total_revenue_baseline = kpiData ? kpiData.total_revenue_baseline : 0;
  const total_revenue_dynamic = kpiData ? kpiData.total_revenue_baseline * displayRatio : 0;
  const revenue_uplift_percent = total_revenue_baseline > 0 
    ? ((total_revenue_dynamic - total_revenue_baseline) / total_revenue_baseline * 100)
    : 0;

  const avg_base_price = kpiData ? kpiData.avg_base_price : 0;
  const avg_dynamic_price = kpiData ? kpiData.avg_base_price * displayRatio : 0;
  const total_units_sold = kpiData ? kpiData.total_units_sold : 0;

  const chartData = kpiData && kpiData.chart_data ? kpiData.chart_data.map(d => ({
    ...d,
    avg_dynamic_price: d.avg_base_price * displayRatio
  })) : [];

  return (
    <>
      <div className="container">
        <header>
          <div className="brand text-gradient">
            <Activity size={32} color="var(--primary-color)" />
            <span>PriceOptima Central</span>
          </div>
          <div className="text-muted">Real-Time Strategy Monitoring</div>
        </header>

        {loadingKpi ? (
          <div className="spinner"></div>
        ) : kpiData && !kpiData.error ? (
          <>
            {/* MVP Tiles */}
            <div className="grid grid-cols-4" style={{ marginBottom: '2rem' }}>
              <div className="glass-panel kpi-card">
                <div className="kpi-title">Total Project Revenue</div>
                <div className="kpi-value">${total_revenue_dynamic.toLocaleString(undefined, {maximumFractionDigits: 2})}</div>
                <div className="kpi-change positive" style={{ color: revenue_uplift_percent < 0 ? 'var(--secondary-color)' : 'var(--accent-color)' }}>
                  <TrendingUp size={16} style={{ transform: revenue_uplift_percent < 0 ? 'rotate(180deg)' : 'none', transition: 'all 0.3s ease' }} /> 
                  {revenue_uplift_percent > 0 ? '+' : ''}{revenue_uplift_percent.toFixed(2)}% vs Baseline
                </div>
              </div>
              <div className="glass-panel kpi-card">
                <div className="kpi-title">Baseline Revenue</div>
                <div className="kpi-value">${total_revenue_baseline.toLocaleString(undefined, {maximumFractionDigits: 2})}</div>
              </div>
              <div className="glass-panel kpi-card">
                <div className="kpi-title">Avg Dynamic Price</div>
                <div className="kpi-value">${avg_dynamic_price.toFixed(2)}</div>
              </div>
              <div className="glass-panel kpi-card">
                <div className="kpi-title">Total Units Sold</div>
                <div className="kpi-value">{total_units_sold.toLocaleString()}</div>
              </div>
            </div>

            {/* Charts Area */}
            <div className="grid grid-cols-3" style={{ marginBottom: '2rem' }}>
              <div className="glass-panel" style={{ gridColumn: 'span 2' }}>
                <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <TrendingUp className="text-gradient" /> 30-Day Price Trends
                </h2>
                <div style={{ height: '300px', width: '100%' }}>
                  <ResponsiveContainer>
                    <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorBase" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="var(--secondary-color)" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="var(--secondary-color)" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorDyn" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="var(--primary-color)" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="var(--primary-color)" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="date" tick={{fontSize: 12}} tickFormatter={(tick) => {
                          const date = new Date(tick);
                          return `${date.getMonth()+1}/${date.getDate()}`;
                      }} />
                      <YAxis domain={['auto', 'auto']} tick={{fontSize: 12}} />
                      <Tooltip content={<CustomTooltip />} />
                      <Area type="monotone" dataKey="avg_base_price" name="Base Price" stroke="var(--secondary-color)" fillOpacity={1} fill="url(#colorBase)" isAnimationActive={true} animationDuration={300} />
                      <Area type="monotone" dataKey="avg_dynamic_price" name="Dynamic Price" stroke="var(--primary-color)" fillOpacity={1} fill="url(#colorDyn)" isAnimationActive={true} animationDuration={300} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Live Simulator */}
              <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
                <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Activity className="text-gradient" /> Live Simulator
                </h2>
                <form onSubmit={handleSimulate} style={{ flex: 1 }}>
                  <div className="input-group">
                    <label className="input-label"><DollarSign size={14} style={{display:'inline', verticalAlign:'middle'}}/> Base Price</label>
                    <input type="number" className="input-field" value={basePrice} onChange={e => setBasePrice(e.target.value)} required />
                  </div>
                  <div className="input-group">
                    <label className="input-label"><Package size={14} style={{display:'inline', verticalAlign:'middle'}}/> Inventory Level</label>
                    <input type="number" className="input-field" value={inventory} onChange={e => setInventory(e.target.value)} required />
                  </div>
                  <div className="input-group">
                    <label className="input-label"><Calendar size={14} style={{display:'inline', verticalAlign:'middle'}}/> Day of Week (0-6)</label>
                    <input type="number" min="0" max="6" className="input-field" value={dayOfWeek} onChange={e => setDayOfWeek(e.target.value)} required />
                  </div>
                  <button type="submit" className="btn" style={{ width: '100%', marginTop: '1rem' }} disabled={simLoading}>
                    {simLoading ? 'Calculating...' : 'Simulate Price'}
                  </button>
                </form>

                {simResult && (
                  <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="text-muted">Optimized Price</span>
                      <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--accent-color)' }}>
                        ${simResult.dynamic_price}
                      </span>
                    </div>
                    {simResult.dynamic_price !== simResult.original_price && (
                      <div style={{ fontSize: '0.875rem', marginTop: '0.5rem', color: simResult.dynamic_price > simResult.original_price ? 'var(--accent-color)' : 'var(--secondary-color)' }}>
                        {simResult.dynamic_price > simResult.original_price ? '▲ Price Increased (High Demand/Low Stock)' : '▼ Price Decreased (Clearance)'}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '4rem' }}>
            <h2>No KPI Data Found</h2>
            <p className="text-muted">{kpiData?.error || "Run the baseline pricing scripts to generate data."}</p>
          </div>
        )}
      </div>
    </>
  );
}

export default App;
