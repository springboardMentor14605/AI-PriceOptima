import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [kpi, setKpi] = useState({});
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    axios.get("http://127.0.0.1:8000/kpi")
      .then(res => setKpi(res.data))
      .catch(err => console.log("KPI Error:", err));

    axios.get("http://127.0.0.1:8000/predictions")
      .then(res => setPredictions(res.data.slice(0, 5)))
      .catch(err => console.log("Prediction Error:", err));
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0f172a, #1e293b)",
      color: "white",
      padding: "30px",
      fontFamily: "Arial"
    }}>

      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: "30px" }}>
        <h1 style={{ fontSize: "42px", marginBottom: "10px" }}>
          AI PriceOptima Dashboard 🚀
        </h1>
        <p style={{ fontSize: "18px", opacity: "0.8" }}>
          Real-Time Dynamic Pricing Intelligence System
        </p>
        <p>{new Date().toLocaleString()}</p>
      </div>

      {/* KPI Cards */}
      <div style={{
        display: "flex",
        gap: "20px",
        justifyContent: "center",
        flexWrap: "wrap"
      }}>

        <div style={cardStyle}>
          <h3>Average Price</h3>
          <h2>{kpi.avg_predicted_price}</h2>
        </div>

        <div style={cardStyle}>
          <h3>Max Price</h3>
          <h2>{kpi.max_price}</h2>
        </div>

        <div style={cardStyle}>
          <h3>Min Price</h3>
          <h2>{kpi.min_price}</h2>
        </div>

        <div style={cardStyle}>
          <h3>Revenue Lift</h3>
          <h2>+12%</h2>
        </div>

        <div style={cardStyle}>
          <h3>AI Status</h3>
          <h2>Active ✅</h2>
        </div>
      </div>

      {/* Refresh Button */}
      <div style={{ textAlign: "center", marginTop: "25px" }}>
        <button
          onClick={loadData}
          style={{
            padding: "12px 25px",
            borderRadius: "12px",
            border: "none",
            background: "#38bdf8",
            color: "white",
            fontSize: "16px",
            cursor: "pointer"
          }}
        >
          Refresh Data
        </button>
      </div>

      {/* AI Recommendation */}
      <div style={sectionStyle}>
        <h2>AI Recommendation Engine 🤖</h2>
        <h3>Suggested Action: Increase Price 🔺</h3>
        <p>Demand trend indicates strong buying behavior.</p>
      </div>

      {/* Revenue Trend */}
      <div style={sectionStyle}>
        <h2>Revenue Trend 📈</h2>
        <h3>Projected Revenue Lift: +12%</h3>
        <p>Compared to static pricing baseline.</p>
      </div>

      {/* Prediction Table */}
      <div style={sectionStyle}>
        <h2>Recent Price Predictions 📊</h2>

        <table style={{
          width: "100%",
          marginTop: "15px",
          borderCollapse: "collapse"
        }}>
          <thead>
            <tr>
              <th style={tableHead}>Product ID</th>
              <th style={tableHead}>Optimal Price</th>
              <th style={tableHead}>Best Model</th>
            </tr>
          </thead>

          <tbody>
            {predictions.map((item, index) => (
              <tr key={index}>
                <td style={tableCell}>{item.product_id}</td>
                <td style={tableCell}>{item.optimal_price}</td>
                <td style={tableCell}>{item.best_model || "XGBoost"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Top Product */}
      <div style={sectionStyle}>
        <h2>Top Opportunity Product 🌟</h2>
        <h3>Product ID: P0013</h3>
        <p>Highest pricing opportunity detected.</p>
      </div>

    </div>
  );
}

const cardStyle = {
  background: "rgba(255,255,255,0.12)",
  padding: "25px",
  borderRadius: "20px",
  minWidth: "220px",
  textAlign: "center",
  backdropFilter: "blur(10px)",
  boxShadow: "0 8px 20px rgba(0,0,0,0.3)"
};

const sectionStyle = {
  marginTop: "30px",
  background: "rgba(255,255,255,0.08)",
  padding: "20px",
  borderRadius: "20px"
};

const tableHead = {
  padding: "12px",
  borderBottom: "1px solid white"
};

const tableCell = {
  padding: "12px",
  textAlign: "center"
};

export default App;