import React, { useState } from 'react';
import { Settings, TrendingUp, AlertCircle } from 'lucide-react';
import axios from 'axios';

const PricingOptimizer = ({ products }) => {
  const [selectedProduct, setSelectedProduct] = useState('');
  const [currentPrice, setCurrentPrice] = useState('');
  const [inventory, setInventory] = useState('');
  const [demandFactor, setDemandFactor] = useState(0.5);
  const [competitorPrice, setCompetitorPrice] = useState('');
  const [season, setSeason] = useState('Summer');
  const [weather, setWeather] = useState('Sunny');
  const [holiday, setHoliday] = useState(false);
  const [discount, setDiscount] = useState(10);
  const [visitors, setVisitors] = useState(50);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleOptimize = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const requestData = {
        current_price: parseFloat(currentPrice),
        inventory: parseInt(inventory),
        demand_factor: parseFloat(demandFactor),
        competitor_price: competitorPrice ? parseFloat(competitorPrice) : null,
        season: season,
        weather: weather,
        holiday: holiday,
        discount: parseInt(discount),
        visitors: parseInt(visitors)
      };

      // Add product details
      if (useCustomProduct) {
        requestData.custom_product = {
          name: customProductName,
          category: customProductCategory
        };
      } else {
        requestData.product_id = parseInt(selectedProduct);
      }

      const response = await axios.post('https://ai-price-optima-pldz.onrender.com/api/pricing/optimize', requestData);
      
      setResult(response.data);
    } catch (error) {
      console.error('Error optimizing price:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProductChange = (productId) => {
    setSelectedProduct(productId);
    const product = products.find(p => p.id === parseInt(productId));
    if (product) {
      setCurrentPrice(product.current_price.toString());
      setInventory(product.inventory.toString());
      setCompetitorPrice(product.competitor_price?.toString() || '');
    }
  };

  const [useCustomProduct, setUseCustomProduct] = useState(false);
  const [customProductName, setCustomProductName] = useState('');
  const [customProductCategory, setCustomProductCategory] = useState('Electronics');

  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Pricing Optimizer</h1>
        <p className="text-gray-600">AI-powered price optimization for maximum revenue</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Optimization Parameters
          </h2>
          
          <form onSubmit={handleOptimize} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Product Selection
              </label>
              <div className="flex items-center space-x-4 mb-3">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="dropdown"
                    checked={!useCustomProduct}
                    onChange={() => setUseCustomProduct(false)}
                    className="mr-2"
                  />
                  <span className="text-sm">Select Existing Product</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="custom"
                    checked={useCustomProduct}
                    onChange={() => setUseCustomProduct(true)}
                    className="mr-2"
                  />
                  <span className="text-sm">Create Custom Product</span>
                </label>
              </div>

              {!useCustomProduct ? (
                <select
                  value={selectedProduct}
                  onChange={(e) => handleProductChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                >
                  <option value="">Select a product</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="space-y-3">
                  <input
                    type="text"
                    value={customProductName}
                    onChange={(e) => setCustomProductName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Product Name"
                    required
                  />
                  <select
                    value={customProductCategory}
                    onChange={(e) => setCustomProductCategory(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="Electronics">Electronics</option>
                    <option value="Furniture">Furniture</option>
                    <option value="Clothing">Clothing</option>
                    <option value="Toys">Toys</option>
                    <option value="Groceries">Groceries</option>
                  </select>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Price (₹)
              </label>
              <input
                type="number"
                step="0.01"
                value={currentPrice}
                onChange={(e) => setCurrentPrice(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Inventory Level
              </label>
              <input
                type="number"
                value={inventory}
                onChange={(e) => setInventory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Demand Factor: {demandFactor.toFixed(2)}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={demandFactor}
                onChange={(e) => setDemandFactor(parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Low</span>
                <span>Medium</span>
                <span>High</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Competitor Price (₹)
              </label>
              <input
                type="number"
                step="0.01"
                value={competitorPrice}
                onChange={(e) => setCompetitorPrice(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Optional"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Season
              </label>
              <select
                value={season}
                onChange={(e) => setSeason(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="Spring">Spring</option>
                <option value="Summer">Summer</option>
                <option value="Autumn">Autumn</option>
                <option value="Winter">Winter</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Weather Condition
              </label>
              <select
                value={weather}
                onChange={(e) => setWeather(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="Sunny">Sunny</option>
                <option value="Cloudy">Cloudy</option>
                <option value="Rainy">Rainy</option>
                <option value="Snowy">Snowy</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Holiday/Promotion
              </label>
              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="true"
                    checked={holiday === true}
                    onChange={() => setHoliday(true)}
                    className="mr-2"
                  />
                  <span className="text-sm">Yes</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="false"
                    checked={holiday === false}
                    onChange={() => setHoliday(false)}
                    className="mr-2"
                  />
                  <span className="text-sm">No</span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Discount (%)
              </label>
              <input
                type="number"
                min="0"
                max="50"
                value={discount}
                onChange={(e) => setDiscount(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Estimated Visitors
              </label>
              <input
                type="number"
                min="0"
                value={visitors}
                onChange={(e) => setVisitors(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Daily visitor count"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full"
            >
              {loading ? 'Optimizing...' : 'Optimize Price'}
            </button>
          </form>
        </div>

        {result && (
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Optimization Results
            </h2>
            
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-700 font-medium">Optimal Price:</span>
                  <span className="text-2xl font-bold text-green-600">
                    ₹{result.optimal_price}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-700 font-medium">Price Change:</span>
                  <span className={`text-lg font-semibold ${
                    result.price_change_percentage > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {result.price_change_percentage > 0 ? '+' : ''}
                    {result.price_change_percentage}%
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Confidence Score:</span>
                  <div className="flex items-center">
                    <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${result.confidence_score * 100}%` }}
                      />
                    </div>
                    <span className="font-medium">
                      {(result.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start">
                  <AlertCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-blue-900 mb-1">AI Reasoning</h4>
                    <p className="text-sm text-blue-800">{result.reasoning}</p>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <h4 className="font-medium text-gray-700 mb-2">Recommendations</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  {result.price_change_percentage > 5 && (
                    <li className="flex items-start">
                      <span className="text-green-500 mr-2">•</span>
                      Consider implementing the price increase gradually
                    </li>
                  )}
                  {result.price_change_percentage < -5 && (
                    <li className="flex items-start">
                      <span className="text-yellow-500 mr-2">•</span>
                      Monitor competitor response to price decrease
                    </li>
                  )}
                  <li className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    Review pricing again in 7 days based on market response
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PricingOptimizer;
