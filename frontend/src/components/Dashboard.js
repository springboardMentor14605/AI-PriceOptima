import React from 'react';
import { TrendingUp, Package, DollarSign } from 'lucide-react';

const Dashboard = ({ analytics }) => {
  const stats = [
    {
      title: 'Total Products',
      value: analytics.total_products || 0,
      icon: Package,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Total Inventory',
      value: analytics.total_inventory || 0,
      icon: Package,
      color: 'bg-green-500',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Average Price',
      value: `₹${analytics.average_price?.toFixed(2) || '0.00'}`,
      icon: DollarSign,
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-100'
    },
    {
      title: 'Revenue Impact',
      value: `${analytics.revenue_impact || 0}%`,
      icon: TrendingUp,
      color: 'bg-purple-500',
      bgColor: 'bg-purple-100'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">AI-powered dynamic pricing system overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
              </div>
              <div className={`${stat.bgColor} p-3 rounded-full`}>
                <stat.icon className={`w-6 h-6 ${stat.color.replace('bg-', 'text-')}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Market Analysis</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Price Optimization Savings</span>
              <span className="text-lg font-semibold text-green-600">
                {analytics.price_optimization_savings || 0}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Revenue Impact</span>
              <span className="text-lg font-semibold text-blue-600">
                {analytics.revenue_impact || 0}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Average Discount Rate</span>
              <span className="text-lg font-semibold text-purple-600">
                {analytics.average_discount_rate || 12.5}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Competitor Price Gap</span>
              <span className="text-lg font-semibold text-orange-600">
                {analytics.competitor_price_gap || 5.2}%
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Dataset Features</h2>
          <div className="space-y-3">
            <div className="border-l-4 border-blue-500 pl-4">
              <h4 className="font-medium text-gray-900">Product Categories</h4>
              <p className="text-sm text-gray-600">Groceries, Toys, Furniture, Clothing, Electronics</p>
            </div>
            <div className="border-l-4 border-green-500 pl-4">
              <h4 className="font-medium text-gray-900">Regional Coverage</h4>
              <p className="text-sm text-gray-600">North, South, East, West regions</p>
            </div>
            <div className="border-l-4 border-purple-500 pl-4">
              <h4 className="font-medium text-gray-900">Market Factors</h4>
              <p className="text-sm text-gray-600">Weather, Holidays, Seasonality, Demand Forecast</p>
            </div>
            <div className="border-l-4 border-orange-500 pl-4">
              <h4 className="font-medium text-gray-900">Business Metrics</h4>
              <p className="text-sm text-gray-600">Inventory, Sales, Visitors, Cost Analysis</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Store Performance</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Store S001</span>
              <span className="font-medium text-green-600">
                +{analytics.store_performance?.S001 || 15.3}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Store S002</span>
              <span className="font-medium text-blue-600">
                +{analytics.store_performance?.S002 || 8.7}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Store S003</span>
              <span className="font-medium text-orange-600">
                +{analytics.store_performance?.S003 || 12.1}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Store S004</span>
              <span className="font-medium text-purple-600">
                +{analytics.store_performance?.S004 || 6.9}%
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Seasonal Trends</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Spring</span>
              <span className="font-medium text-green-600">
                {analytics.seasonal_trends?.Spring || 'High'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Summer</span>
              <span className="font-medium text-blue-600">
                {analytics.seasonal_trends?.Summer || 'Peak'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Autumn</span>
              <span className="font-medium text-orange-600">
                {analytics.seasonal_trends?.Autumn || 'Medium'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Winter</span>
              <span className="font-medium text-purple-600">
                {analytics.seasonal_trends?.Winter || 'Low'}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Weather Impact</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Sunny</span>
              <span className="font-medium text-yellow-600">
                +{analytics.weather_impact?.Sunny || 18}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Cloudy</span>
              <span className="font-medium text-gray-600">
                +{analytics.weather_impact?.Cloudy || 5}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Rainy</span>
              <span className="font-medium text-blue-600">
                {analytics.weather_impact?.Rainy || -8}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Snowy</span>
              <span className="font-medium text-cyan-600">
                {analytics.weather_impact?.Snowy || -15}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
