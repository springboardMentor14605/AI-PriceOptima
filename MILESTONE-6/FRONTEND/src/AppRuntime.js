import React, { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, BarChart2, Target, Zap } from "lucide-react";
import "./index.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function AppRuntime() {
  const [tab, setTab] = useState("dashboard");
  const [kpi, setKpi] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [elasticity, setElasticity] = useState(null);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    price: 75,
    cost: 50,
    competitor_price: 80,
  });

  useEffect(() => {
    fetchKpi();
    const intervalId = setInterval(fetchKpi, 30000);
    return () => clearInterval(intervalId);
  }, []);

  async function fetchKpi() {
    try {
      const response = await fetch(`${API_URL}/kpi/dashboard`);
      const data = await response.json();
      setKpi(data);
    } catch (error) {
      console.error("Failed to fetch KPI data", error);
    }
  }

  async function runPrediction() {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          discount_pct: 10,
          inventory_units: 100,
          category: 1,
          region: 0,
          seasonality: 1,
          weather_condition: 0,
          month: 4,
          day_of_week: 2,
        }),
      });
      const data = await response.json();
      setPrediction(data);
    } catch (error) {
      console.error("Prediction failed", error);
    } finally {
      setLoading(false);
    }
  }

  async function runElasticity() {
    setLoading(true);
    try {
      const response = await fetch(
        `${API_URL}/experiment/elasticity?base_price=${form.price}&price_range=0.3&steps=20`
      );
      const data = await response.json();
      setElasticity(data);
      setTab("analytics");
    } catch (error) {
      console.error("Elasticity analysis failed", error);
    } finally {
      setLoading(false);
    }
  }

  const chartData = elasticity
    ? elasticity.data_points.prices.map((price, index) => ({
        price: price.toFixed(2),
        demand: Math.round(elasticity.data_points.demands[index]),
        revenue: Math.round(elasticity.data_points.revenues[index]),
      }))
    : [];

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">PriceOptima</p>
          <h1>Dynamic pricing dashboard</h1>
          <p className="subtle">
            FastAPI backend plus a React dashboard for KPI tracking, demand
            prediction, and elasticity analysis.
          </p>
        </div>
      </header>

      <nav className="tab-row">
        <button
          className={tab === "dashboard" ? "tab active" : "tab"}
          onClick={() => setTab("dashboard")}
        >
          <Activity size={16} /> Dashboard
        </button>
        <button
          className={tab === "predict" ? "tab active" : "tab"}
          onClick={() => setTab("predict")}
        >
          <Target size={16} /> Predict
        </button>
        <button
          className={tab === "analytics" ? "tab active" : "tab"}
          onClick={() => setTab("analytics")}
        >
          <BarChart2 size={16} /> Analytics
        </button>
      </nav>

      {tab === "dashboard" && (
        <section className="panel-stack">
          <div className="card-grid">
            <article className="card">
              <span className="label">Revenue</span>
              <strong>{kpi ? `INR ${kpi.revenue.total.toLocaleString()}` : "Loading..."}</strong>
            </article>
            <article className="card">
              <span className="label">Units Sold</span>
              <strong>{kpi ? kpi.demand.total_units.toLocaleString() : "Loading..."}</strong>
            </article>
            <article className="card">
              <span className="label">Forecast Accuracy</span>
              <strong>{kpi ? `${kpi.demand.forecast_accuracy}%` : "Loading..."}</strong>
            </article>
            <article className="card">
              <span className="label">ML Lift</span>
              <strong>{kpi ? `+${kpi.revenue.ml_lift}%` : "Loading..."}</strong>
            </article>
          </div>

          <section className="chart-panel">
            <div className="panel-title">Revenue trend</div>
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={[
                    { day: "Mon", revenue: 120000 },
                    { day: "Tue", revenue: 140000 },
                    { day: "Wed", revenue: 180000 },
                    { day: "Thu", revenue: 200000 },
                    { day: "Fri", revenue: 220000 },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#293145" />
                  <XAxis dataKey="day" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip />
                  <Area type="monotone" dataKey="revenue" stroke="#f97316" fill="#fdba74" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>
        </section>
      )}

      {tab === "predict" && (
        <section className="two-col">
          <article className="card">
            <div className="panel-title">Pricing inputs</div>
            <label className="field">
              <span>Price</span>
              <input
                type="number"
                value={form.price}
                onChange={(event) =>
                  setForm({ ...form, price: Number(event.target.value) })
                }
              />
            </label>
            <label className="field">
              <span>Cost</span>
              <input
                type="number"
                value={form.cost}
                onChange={(event) =>
                  setForm({ ...form, cost: Number(event.target.value) })
                }
              />
            </label>
            <label className="field">
              <span>Competitor Price</span>
              <input
                type="number"
                value={form.competitor_price}
                onChange={(event) =>
                  setForm({
                    ...form,
                    competitor_price: Number(event.target.value),
                  })
                }
              />
            </label>
            <div className="action-row">
              <button className="primary" onClick={runPrediction}>
                <Zap size={16} /> {loading ? "Working..." : "Predict"}
              </button>
              <button className="secondary" onClick={runElasticity}>
                Run Elasticity
              </button>
            </div>
          </article>

          <article className="card">
            <div className="panel-title">Prediction output</div>
            {prediction ? (
              <div className="result-grid">
                <p>Demand: {prediction.predicted_demand}</p>
                <p>Revenue: INR {Math.round(prediction.expected_revenue).toLocaleString()}</p>
                <p>Profit: {prediction.profit_margin.toFixed(1)}%</p>
                <p>Recommended: INR {prediction.recommended_price.toFixed(2)}</p>
              </div>
            ) : (
              <p className="subtle">
                Run a prediction to see demand, revenue, profit margin, and the
                recommended price.
              </p>
            )}
          </article>
        </section>
      )}

      {tab === "analytics" && (
        <section className="chart-panel">
          <div className="panel-title">Elasticity analysis</div>
          {elasticity ? (
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#293145" />
                  <XAxis dataKey="price" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip />
                  <Line type="monotone" dataKey="revenue" stroke="#f97316" strokeWidth={2} />
                  <Line type="monotone" dataKey="demand" stroke="#22c55e" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="subtle">Run elasticity analysis from the Predict tab to populate this chart.</p>
          )}
        </section>
      )}
    </div>
  );
}
