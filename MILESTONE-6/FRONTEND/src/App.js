import React, { useState, useEffect } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, CartesianGrid } from 'recharts';
import { Activity, Zap, BarChart2, TrendingUp } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export default function App() {
  const [tab, setTab] = useState('dashboard');
  const [kpi, setKpi] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [elasticity, setElasticity] = useState(null);
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    price: 75,
    cost: 50,
    competitor_price: 80
  });

  useEffect(() => {
    fetchKPI();
    const i = setInterval(fetchKPI, 30000);
    return () => clearInterval(i);
  }, []);

  const fetchKPI = async () => {
    try {
      const res = await fetch(`${API_URL}/kpi/dashboard`);
      const data = await res.json();
      setKpi(data);
    } catch (e) {
      console.error(e);
    }
  };

  const predict = async () => {
    setLoading(true);
    const res = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...form,
        discount_pct: 10,
        inventory_units: 100,
        category: 1,
        region: 0,
        seasonality: 1,
        weather_condition: 0,
        month: 4,
        day_of_week: 2
      })
    });
    const data = await res.json();
    setPrediction(data);
    setLoading(false);
  };

  const runElasticity = async () => {
    setLoading(true);
    const res = await fetch(`${API_URL}/experiment/elasticity?base_price=${form.price}&price_range=0.3&steps=20`);
    const data = await res.json();
    setElasticity(data);
    setLoading(false);
  };

  const chartData = elasticity ? elasticity.data_points.prices.map((p, i) => ({
    price: p.toFixed(2),
    demand: elasticity.data_points.demands[i],
    revenue: elasticity.data_points.revenues[i]
  })) : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-6">
      <h1 className="text-3xl font-bold mb-6">🚀 PriceOptima Final Dashboard</h1>

      <div className="flex gap-3 mb-6">
        <Button onClick={() => setTab('dashboard')}>Dashboard</Button>
        <Button onClick={() => setTab('predict')}>Predict</Button>
        <Button onClick={() => setTab('analytics')}>Analytics</Button>
      </div>

      {tab === 'dashboard' && kpi && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="grid md:grid-cols-4 gap-4">
            <Card><CardContent>Revenue ₹{kpi.revenue.total}</CardContent></Card>
            <Card><CardContent>Units {kpi.demand.total_units}</CardContent></Card>
            <Card><CardContent>Accuracy {kpi.demand.forecast_accuracy}%</CardContent></Card>
            <Card><CardContent>ML Lift +{kpi.revenue.ml_lift}%</CardContent></Card>
          </div>

          <div className="mt-6 h-72">
            <ResponsiveContainer>
              <AreaChart data={[
                { d: 'Mon', r: 120000 },
                { d: 'Tue', r: 140000 },
                { d: 'Wed', r: 180000 },
                { d: 'Thu', r: 200000 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="d" />
                <YAxis />
                <Tooltip />
                <Area dataKey="r" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      )}

      {tab === 'predict' && (
        <div className="grid md:grid-cols-2 gap-4">
          <Card>
            <CardContent className="space-y-3">
              <Input placeholder="Price" value={form.price} onChange={e => setForm({ ...form, price: +e.target.value })} />
              <Input placeholder="Cost" value={form.cost} onChange={e => setForm({ ...form, cost: +e.target.value })} />
              <Input placeholder="Competitor Price" value={form.competitor_price} onChange={e => setForm({ ...form, competitor_price: +e.target.value })} />
              <Button onClick={predict}>{loading ? 'Loading...' : 'Predict'}</Button>
              <Button onClick={runElasticity}>Run Elasticity</Button>
            </CardContent>
          </Card>

          {prediction && (
            <Card>
              <CardContent>
                <p>Demand: {prediction.predicted_demand}</p>
                <p>Revenue: ₹{prediction.expected_revenue}</p>
                <p>Profit: {prediction.profit_margin.toFixed(1)}%</p>
                <p>Recommended: ₹{prediction.recommended_price}</p>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {tab === 'analytics' && elasticity && (
        <div className="h-96">
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="price" />
              <YAxis />
              <Tooltip />
              <Line dataKey="revenue" />
              <Line dataKey="demand" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {tab === 'analytics' && !elasticity && (
        <div className="text-center opacity-70">
          <BarChart2 size={48} />
          <p>Run elasticity to view analytics</p>
        </div>
      )}
    </div>
  );
}