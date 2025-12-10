import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom'; // Use Link for navigation
import './App.css'; // Assuming you have a CSS file for styling

interface MessageResponse {
  Hello: string;
}

const App = () => {
  const [message, setMessage] = useState("Connecting...");

  // Effect to fetch the "Hello" message from the FastAPI root endpoint
  useEffect(() => {
    // Calling the API via the Nginx proxy path
    axios.get<MessageResponse>('/api/') 
      .then(response => {
        setMessage(response.data.Hello);
      })
      .catch(error => {
        console.error("Error fetching data:", error);
        setMessage("API Connection Failed!");
      });
  }, []);

  return (
    <div className="home-container">
      <header className="app-header">
        <h1>✨ AutoDev Spidey ✨</h1>
        <nav>
          {/* Link to the login page */}
          <Link to="/login" className="login-button">Login</Link> 
        </nav>
      </header>

      <main className="content-area">
        <h2>Your Full-Stack Application is Running</h2>
        <p>This message is from the FastAPI backend (via Docker/Nginx):</p>
        <div className={`api-status ${message === "API Connection Failed!" ? 'error' : 'success'}`}>
          <strong>API Status:</strong> {message}
        </div>
        
        <p>Go to the Login page to test the authentication feature.</p>
        <p>FastAPI Docs: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">http://localhost:8000/docs</a></p>
      </main>
    </div>
  );
};

export default App;