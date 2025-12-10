import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';       // This will be our Home Page
import LoginComponent from './pages/LoginPage'; // We will create this
import './index.css'; // Assuming a basic CSS file exists

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        {/* The main route for the application */}
        <Route path="/" element={<App />} /> 
        
        {/* The dedicated route for the login page */}
        <Route path="/login" element={<LoginComponent />} /> 
        
        {/* You can add a 404/NotFound component here later */}
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);