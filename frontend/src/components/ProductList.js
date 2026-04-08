import React, { useState } from 'react';
import { Eye } from 'lucide-react';
import axios from 'axios';

const ProductList = ({ products, onRefresh }) => {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleOptimizePrice = async (product) => {
    setLoading(true);
    try {
      const response = await axios.post('https://ai-price-optima-pldz.onrender.com/api/pricing/optimize', {
        product_id: product.id,
        current_price: product.current_price,
        inventory: product.inventory,
        demand_factor: 0.7, // Mock value
        competitor_price: product.competitor_price
      });
      
      setSelectedProduct({
        ...product,
        optimization: response.data
      });
    } catch (error) {
      console.error('Error optimizing price:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Products</h1>
          <p className="text-gray-600">Manage your product catalog and pricing</p>
        </div>
        <button 
          onClick={onRefresh}
          className="btn btn-primary"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          {products.map((product) => (
            <div key={product.id} className="card">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
                  <div className="mt-2 space-y-1">
                    <p className="text-sm text-gray-600">
                      Current Price: <span className="font-medium text-gray-900">₹{product.current_price}</span>
                    </p>
                    <p className="text-sm text-gray-600">
                      Inventory: <span className="font-medium text-gray-900">{product.inventory} units</span>
                    </p>
                    {product.competitor_price && (
                      <p className="text-sm text-gray-600">
                        Competitor Price: <span className="font-medium text-gray-900">₹{product.competitor_price}</span>
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleOptimizePrice(product)}
                    disabled={loading}
                    className="btn btn-primary text-sm"
                  >
                    {loading ? 'Analyzing...' : 'Optimize Price'}
                  </button>
                  <button
                    onClick={() => setSelectedProduct(product)}
                    className="btn btn-secondary text-sm"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {selectedProduct && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {selectedProduct.name} - Details
            </h3>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Price History</h4>
                <div className="space-y-1">
                  {selectedProduct.sales_history.map((price, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-gray-600">Period {index + 1}</span>
                      <span className="font-medium">₹{price}</span>
                    </div>
                  ))}
                </div>
              </div>

              {selectedProduct.optimization && (
                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-700 mb-2">Optimization Results</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Optimal Price:</span>
                      <span className="font-semibold text-green-600">
                        ₹{selectedProduct.optimization.optimal_price}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Price Change:</span>
                      <span className={`font-semibold ${
                        selectedProduct.optimization.price_change_percentage > 0 
                          ? 'text-green-600' 
                          : 'text-red-600'
                      }`}>
                        {selectedProduct.optimization.price_change_percentage > 0 ? '+' : ''}
                        {selectedProduct.optimization.price_change_percentage}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Confidence:</span>
                      <span className="font-medium">
                        {(selectedProduct.optimization.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="mt-2 p-3 bg-gray-50 rounded text-sm text-gray-600">
                      <strong>Reasoning:</strong> {selectedProduct.optimization.reasoning}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductList;
