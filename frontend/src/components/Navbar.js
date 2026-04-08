import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { TrendingUp, Package, Settings, Home } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-8 h-8 text-primary-600" />
            <span className="text-2xl font-bold text-gray-800">AI PriceOptima</span>
          </div>
          
          <div className="flex space-x-6">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                isActive('/') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
              }`}
            >
              <Home className="w-5 h-5" />
              <span>Dashboard</span>
            </Link>
            
            <Link
              to="/products"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                isActive('/products') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
              }`}
            >
              <Package className="w-5 h-5" />
              <span>Products</span>
            </Link>
            
            <Link
              to="/pricing"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                isActive('/pricing') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
              }`}
            >
              <Settings className="w-5 h-5" />
              <span>Pricing</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
