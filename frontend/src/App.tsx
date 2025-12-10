// frontend/src/App.tsx

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import './App.css';

interface MessageResponse {
  Hello: string;
}

const App: React.FC = () => {
  const [message, setMessage] = useState('Connecting...');

  useEffect(() => {
    axios
      .get<MessageResponse>('http://localhost:8000/')
      .then((response) => {
        setMessage(response.data.Hello);
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
        setMessage('API Connection Failed!');
      });
  }, []);

  const isError = message === 'API Connection Failed!';

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-inner">
          <h1 className="app-title">✨ AutoDev Spidey POC ✨</h1>
          <nav className="app-nav">
            <Link to="/login" className="btn btn-primary">
              Login / Sign Up
            </Link>
          </nav>
        </div>
      </header>

      <main className="app-main">
        <section className="card status-card">
          <h2 className="card-title">System Status Check</h2>
          <p className="card-subtitle">
            This message confirms the Docker / Nginx / FastAPI backend is live:
          </p>

          <div
            className={`status-banner ${
              isError ? 'status-banner--error' : 'status-banner--ok'
            }`}
          >
            <span className="status-label">
              {isError ? 'Backend Status: Error' : 'Backend Status: Active'}
            </span>
            <span className="status-message">{message}</span>
          </div>

          <p className="card-text">
            Ready to test the authentication features or review the backend documentation.
          </p>

          <div className="card-actions">
            <Link to="/login" className="btn btn-primary btn-full-mobile">
              Go to Login Page
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-outline"
            >
              View FastAPI Docs
            </a>
          </div>
        </section>
      </main>
    </div>
  );
};

export default App;
