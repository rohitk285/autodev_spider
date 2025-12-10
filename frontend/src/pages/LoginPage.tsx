import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';
//import axios from 'axios';

const LoginComponent: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // NOTE: In a real app, you would send a POST request to a /token or /login endpoint.
    // For this initial setup, we'll just log the attempt and navigate.
    
    console.log(`Attempting login for: ${username}`);

    try {
        // --- REAL API CALL Placeholder ---
        // await axios.post('/api/token', { username, password });
        // ---
        
        // Simulating a successful login
        if (username && password) {
             alert(`Login successful for ${username}! (Simulated)`);
             navigate('/'); // Redirect to home page on success
        } else {
            setError("Please enter both username and password.");
        }
        
    } catch (err) {
        setError('Login failed. Please check your credentials.');
    }
  };

  return (
    <div className="login-container">
      <h2>User Login</h2>
      <form className="login-form" onSubmit={handleSubmit}>
        
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        
        {error && <p className="error-message">{error}</p>}
        
        <button type="submit" className="login-submit-button">Log In</button>
      </form>
      <p className="back-link"><Link to="/">← Back to Home</Link></p>
    </div>
  );
};

export default LoginComponent;