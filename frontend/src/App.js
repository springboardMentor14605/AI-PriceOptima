import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import ProductList from './components/ProductList';
import PricingOptimizer from './components/PricingOptimizer';
import axios from 'axios';

function App() {
  const [products, setProducts] = useState([]);
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    fetchProducts();
    fetchAnalytics();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get('https://ai-price-optima-pldz.onrender.com/api/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get('https://ai-price-optima-pldz.onrender.com/api/analytics/dashboard');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route 
              path="/" 
              element={<Dashboard analytics={analytics} />} 
            />
            <Route 
              path="/products" 
              element={<ProductList products={products} onRefresh={fetchProducts} />} 
            />
            <Route 
              path="/pricing" 
              element={<PricingOptimizer products={products} />} 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
