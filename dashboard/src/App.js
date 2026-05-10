import React, { useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar
} from "recharts";

function App() {

  const [formData, setFormData] = useState({
    inventory_level: "",
    units_sold: "",
    demand_forecast: "",
    competitor_pricing: "",
    discount: "",
    visitors: "",
    profit_margin: "",
    conversion_rate: "",
  });

  const [prediction, setPrediction] = useState(null);
  const [recommendation, setRecommendation] = useState("");
  const [revenueLift, setRevenueLift] = useState(null);

  // Handle input
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value === "" ? 0 : parseFloat(e.target.value)
    });
  };

  // API call
  const handleSubmit = () => {
  console.log("Sending:", formData);

  axios.post("http://127.0.0.1:8000/predict", formData)
    .then(res => {
      console.log("Response:", res.data);

      if (res.data.predicted_price !== undefined) {
        setPrediction(res.data.predicted_price);
        setRecommendation(res.data.recommendation);
        setRevenueLift(res.data.revenue_lift);
      } else {
        alert("Prediction failed!");
      }
    })
    .catch(err => {
      console.log("ERROR:", err);
      alert("Backend error!");
    });
};

  // 📈 Graph data
  const trendData = [
    { name: "Low Demand", price: prediction * 0.8 },
    { name: "Normal", price: prediction },
    { name: "High Demand", price: prediction * 1.2 }
  ];

  const compareData = [
    { name: "Competitor", price: formData.competitor_pricing },
    { name: "AI Price", price: prediction }
  ];

  return (
    <div style={{
      minHeight: "100vh",
      padding: "30px",
      background: "linear-gradient(135deg, #0f172a, #1e293b)",
      color: "white",
      fontFamily: "Arial"
    }}>

      <h1 style={{ textAlign: "center" }}>AI PriceOptima 🚀</h1>

      <h2>Enter Product Details</h2>

      {Object.keys(formData).map((key) => (
        <div key={key}>
          <label>{key}</label>
          <input
            type="number"
            name={key}
            onChange={handleChange}
            style={{ margin: "5px", padding: "8px", width: "200px" }}
          />
        </div>
      ))}

      <button onClick={handleSubmit} style={{
        marginTop: "15px",
        padding: "10px 20px",
        background: "#38bdf8",
        border: "none",
        borderRadius: "10px",
        cursor: "pointer"
      }}>
        Predict Price
      </button>

      {prediction !== null && (
        <>
          <h2>Predicted Price: ₹{prediction}</h2>
          <h3>Recommendation: {recommendation}</h3>
          <h3>Revenue Lift: {revenueLift}%</h3>

          {/* 📈 Trend Graph */}
          <div style={{ marginTop: "30px" }}>
            <h3>Demand vs Price Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" stroke="#fff"/>
                <YAxis stroke="#fff"/>
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="#38bdf8" strokeWidth={3}/>
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* 📊 Comparison Graph */}
          <div style={{ marginTop: "30px" }}>
            <h3>Competitor vs AI Price</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={compareData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" stroke="#fff"/>
                <YAxis stroke="#fff"/>
                <Tooltip />
                <Bar dataKey="price" fill="#38bdf8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}

    </div>
  );
}

export default App;