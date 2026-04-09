import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Package, 
  MapPin, 
  Tag, 
  Settings, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle,
  RefreshCw,
  BarChart3,
  ChevronRight,
  Zap
} from 'lucide-react';

const CATEGORIES = ['Clothing', 'Electronics', 'Furniture', 'Groceries', 'Toys'];
const REGIONS = ['East', 'North', 'South', 'West'];

function App() {
  const [formData, setFormData] = useState({
    category: 'Electronics',
    region: 'South',
    inventory_level: 15,
    price: 450.0
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    checkBackend();
  }, []);

  const checkBackend = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setApiStatus('online');
      } else {
        setApiStatus('error');
      }
    } catch (err) {
      setApiStatus('offline');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'inventory_level' || name === 'price' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/recommend-price', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recommendation from server');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary-600 p-2 rounded-lg">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent">
              PriceOptima
            </h1>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 text-sm text-slate-500 font-medium">
              <span className={`w-2 h-2 rounded-full ${
                apiStatus === 'online' ? 'bg-emerald-500' : 
                apiStatus === 'offline' ? 'bg-red-500' : 'bg-amber-500'
              }`}></span>
              Backend: {apiStatus.charAt(0).toUpperCase() + apiStatus.slice(1)}
            </div>
            <button 
              onClick={checkBackend}
              className="p-2 text-slate-400 hover:text-primary-600 transition-colors"
              title="Refresh status"
            >
              <RefreshCw className={`w-4 h-4 ${apiStatus === 'checking' ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Input Panel */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
                <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                  <Settings className="w-4 h-4 text-primary-500" />
                  Parameters
                </h2>
              </div>
              
              <form onSubmit={handleSubmit} className="p-6 space-y-5">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    Product Category
                  </label>
                  <div className="relative">
                    <Tag className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <select 
                      name="category"
                      value={formData.category}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all outline-none appearance-none"
                    >
                      {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    Region
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <select 
                      name="region"
                      value={formData.region}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all outline-none appearance-none"
                    >
                      {REGIONS.map(reg => <option key={reg} value={reg}>{reg}</option>)}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 leading-tight">
                    Inventory Level
                    <span className="float-right text-primary-600 normal-case">{formData.inventory_level} units</span>
                  </label>
                  <div className="relative pt-2">
                    <Package className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
                    <input 
                      type="range"
                      name="inventory_level"
                      min="0"
                      max="500"
                      value={formData.inventory_level}
                      onChange={handleInputChange}
                      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-primary-600 mb-2"
                    />
                    <input 
                      type="number"
                      name="inventory_level"
                      value={formData.inventory_level}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 leading-tight">
                    Current Price ($)
                  </label>
                  <input 
                    type="number"
                    name="price"
                    step="0.01"
                    value={formData.price}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-primary-500 outline-none transition-all font-medium text-lg text-slate-700"
                  />
                </div>

                <button 
                  type="submit"
                  disabled={loading || apiStatus === 'offline'}
                  className="w-full py-4 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white rounded-xl font-bold shadow-lg shadow-primary-200 transition-all flex items-center justify-center gap-2 group mt-4"
                >
                  {loading ? (
                    <RefreshCw className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      Optimize Prices
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>
              </form>
            </div>

            {error && (
              <div className="p-4 bg-red-50 border border-red-100 rounded-2xl flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
                <p className="text-sm text-red-600 font-medium">{error}</p>
              </div>
            )}
          </div>

          {/* Results Area */}
          <div className="lg:col-span-8 flex flex-col gap-8">
            {!result && !loading && !error && (
              <div className="flex-1 min-h-[400px] border-2 border-dashed border-slate-200 rounded-3xl flex flex-col items-center justify-center text-slate-400 p-8 text-center">
                <div className="bg-slate-100 p-6 rounded-full mb-6">
                  <BarChart3 className="w-12 h-12 text-slate-300" />
                </div>
                <h3 className="text-xl font-semibold text-slate-600 mb-2">Ready for Optimization</h3>
                <p className="max-w-xs text-sm">
                  Adjust parameters on the left and click "Optimize Prices" to receive ML-driven recommendations.
                </p>
              </div>
            )}

            {result && (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-700 space-y-8">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Baseline Recommendation */}
                  <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                      <Zap className="w-24 h-24 text-slate-900" />
                    </div>
                    <div className="flex items-center gap-2 text-slate-500 font-medium mb-4">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      Rule-Based Baseline
                    </div>
                    <div className="text-4xl font-black text-slate-900 mb-1">
                      ${result.baseline_recommendation.toFixed(2)}
                    </div>
                    <div className="text-sm text-slate-400 flex items-center gap-1">
                      Current: ${result.current_state.current_price.toFixed(2)} 
                      <ChevronRight className="w-3 h-3" />
                      {((result.baseline_recommendation / result.current_state.current_price - 1) * 100).toFixed(1)}% change
                    </div>
                  </div>

                  {/* ML Suggestion */}
                  <div className="bg-primary-600 p-6 rounded-3xl shadow-xl shadow-primary-200 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                      <TrendingUp className="w-24 h-24 text-white" />
                    </div>
                    <div className="flex items-center gap-2 text-primary-100 font-medium mb-4">
                      <Zap className="w-4 h-4 text-amber-300 fill-amber-300" />
                      ML-Driven Suggestion
                    </div>
                    <div className="text-4xl font-black text-white mb-1">
                      ${result.ml_recommendations.xgb_suggested_price.toFixed(2)}
                    </div>
                    <div className="text-sm text-primary-100/70 flex items-center gap-1 font-medium">
                      Current: ${result.current_state.current_price.toFixed(2)} 
                      <ChevronRight className="w-3 h-3" />
                      {((result.ml_recommendations.xgb_suggested_price / result.current_state.current_price - 1) * 100).toFixed(1)}% change
                    </div>
                  </div>
                </div>

                {/* Model Comparison Table */}
                <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm">
                  <div className="px-8 py-5 border-b border-slate-100 flex items-center justify-between">
                    <h3 className="font-bold text-slate-800">Advanced ML Metrics</h3>
                    <div className="text-xs font-bold text-primary-600 bg-primary-50 px-3 py-1 rounded-full uppercase tracking-wider">
                      Confidence Level: High
                    </div>
                  </div>
                  <div className="p-0 overflow-x-auto">
                    <table className="w-full text-left">
                      <thead className="bg-slate-50 text-xs font-bold text-slate-500 uppercase tracking-widest border-b border-slate-100">
                        <tr>
                          <th className="px-8 py-4">Predictive Model</th>
                          <th className="px-8 py-4">Predicted Demand (Units)</th>
                          <th className="px-8 py-4">Price Action</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                        <tr className="hover:bg-slate-50/50 transition-colors">
                          <td className="px-8 py-6 font-semibold text-slate-700">XGBoost Ensemble</td>
                          <td className="px-8 py-6 font-mono text-lg text-slate-600">
                            {result.ml_recommendations.predicted_demand_xgb}
                          </td>
                          <td className="px-8 py-6">
                            <span className="inline-flex items-center gap-1 text-sm font-bold text-primary-600 bg-primary-50 px-3 py-1 rounded-lg">
                              {result.ml_recommendations.predicted_demand_xgb > result.current_state.inventory ? 'Upward Premium' : 
                               result.ml_recommendations.predicted_demand_xgb < (result.current_state.inventory * 0.1) ? 'Volume Liquidation' : 'Market Balanced'}
                            </span>
                          </td>
                        </tr>
                        <tr className="hover:bg-slate-50/50 transition-colors">
                          <td className="px-8 py-6 font-semibold text-slate-700">LightGBM Gradient Booster</td>
                          <td className="px-8 py-6 font-mono text-lg text-slate-600">
                            {result.ml_recommendations.predicted_demand_lgb}
                          </td>
                          <td className="px-8 py-6">
                            <span className="text-sm font-medium text-slate-400 italic">Complementary insight</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <div className="px-8 py-4 bg-slate-50/50 border-t border-slate-100">
                    <p className="text-xs text-slate-400 leading-relaxed font-medium">
                      * Recommendations are calculated based on current inventory pressure ({result.current_state.inventory} units) 
                      and predictive demand analysis. Model suggests a {result.ml_recommendations.xgb_suggested_price > result.current_state.current_price ? 'price increase' : 'discount'} 
                      to maximize balance between profit and turnover.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto py-12 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm text-slate-400 font-medium">
            AI: PriceOptima &bull; Enterprise Dynamic Pricing Intelligence &bull; © 2026
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
