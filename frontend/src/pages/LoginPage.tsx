// frontend/src/pages/LoginPage.tsx

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login, register } from '../services/authService';
import './LoginPage.css';

const LoginComponent: React.FC = () => {
  // --- State for Toggling Forms ---
  const [isRegistering, setIsRegistering] = useState(false);

  // --- State for Forms ---
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState(''); // Registration only

  // --- UI Feedback State ---
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const navigate = useNavigate();

  // --- Utility to clear fields ---
  const clearFields = () => {
    setUsername('');
    setEmail('');
    setPassword('');
    setConfirmPassword('');
  };

  const clearStatus = () => {
    setError(null);
    setMessage(null);
  };

  const resetForm = () => {
    clearFields();
    clearStatus();
  };

  // --- Handlers ---

  const handleRegistrationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    if (password !== confirmPassword) {
      return setError('Passwords do not match.');
    }

    try {
      const newUser = await register(username, email, password, confirmPassword);

      setMessage(`Registration successful for ${newUser.username}! Please log in.`);
      setIsRegistering(false);
      clearFields(); // keep success message visible

    } catch (err: any) {
      setError(err.message || 'Registration failed due to an unknown error.');
    }
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);

    try {
      const { userId } = await login(username, password);
      console.log(userId);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed. Check username and password.');
    }
  };

  // --- Render Forms ---

  const renderLoginForm = () => (
    <form className="auth-form" onSubmit={handleLoginSubmit}>
      <h2 className="form-title">Sign in to your account</h2>
      <p className="form-subtitle">Welcome back! Please enter your details.</p>

      <div className="input-group">
        <label className="input-label" htmlFor="login-username">
          Username or Email
        </label>
        <input
          id="login-username"
          type="text"
          placeholder="e.g. spidey_dev"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="form-input"
        />
      </div>

      <div className="input-group">
        <label className="input-label" htmlFor="login-password">
          Password
        </label>
        <input
          id="login-password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="form-input"
        />
      </div>

      {error && <p className="feedback-message feedback-message--error">{error}</p>}

      <button type="submit" className="btn btn-primary auth-submit-btn">
        Log In
      </button>

      <p className="form-switch">
        Need an account?{' '}
        <button
          type="button"
          className="switch-link-text"
          onClick={() => {
            setIsRegistering(true);
            clearStatus();
          }}
        >
          Register here
        </button>
      </p>
    </form>
  );

  const renderRegisterForm = () => (
    <form className="auth-form" onSubmit={handleRegistrationSubmit}>
      <h2 className="form-title">Create a new account</h2>
      <p className="form-subtitle">Join AutoDev Spidey and start exploring.</p>

      <div className="input-group">
        <label className="input-label" htmlFor="register-username">
          Username
        </label>
        <input
          id="register-username"
          type="text"
          placeholder="e.g. spidey_dev"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          className="form-input"
        />
      </div>

      <div className="input-group">
        <label className="input-label" htmlFor="register-email">
          Email
        </label>
        <input
          id="register-email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="form-input"
        />
      </div>

      <div className="input-group">
        <label className="input-label" htmlFor="register-password">
          Password
        </label>
        <input
          id="register-password"
          type="password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="form-input"
        />
      </div>

      <div className="input-group">
        <label className="input-label" htmlFor="register-confirm-password">
          Confirm Password
        </label>
        <input
          id="register-confirm-password"
          type="password"
          placeholder="••••••••"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          className="form-input"
        />
      </div>

      {error && <p className="feedback-message feedback-message--error">{error}</p>}

      <button type="submit" className="btn btn-primary auth-submit-btn">
        Sign Up
      </button>

      <p className="form-switch">
        Already have an account?{' '}
        <button
          type="button"
          className="switch-link-text"
          onClick={() => {
            setIsRegistering(false);
            clearStatus();
          }}
        >
          Login
        </button>
      </p>
    </form>
  );

  return (
    <div className="page-wrapper auth-page-wrapper">
      <div className="auth-page-inner">
        <div className="auth-header-row">
          <p className="back-link">
            <Link to="/" className="back-link-text">
              ← Back to Home
            </Link>
          </p>
        </div>

        {message && (
          <div className="feedback-message feedback-message--success">{message}</div>
        )}

        <div className="auth-layout">
          <section className="auth-hero">
            <h1 className="auth-hero-title">AutoDev Spidey Access</h1>
            <p className="auth-hero-text">
              Sign in or create an account to interact with the AutoDev Spidey POC dashboard,
              test authentication flows, and explore the backend features.
            </p>
            <ul className="auth-hero-list">
              <li>JWT-based authentication</li>
              <li>FastAPI backend integration</li>
              <li>Docker / Nginx / CI-friendly setup</li>
            </ul>
          </section>

          <section className="auth-card">
            <div className="auth-toggle">
              <button
                type="button"
                className={`auth-toggle-btn ${!isRegistering ? 'auth-toggle-btn--active' : ''}`}
                onClick={() => {
                  setIsRegistering(false);
                  resetForm();
                }}
              >
                Login
              </button>
              <button
                type="button"
                className={`auth-toggle-btn ${isRegistering ? 'auth-toggle-btn--active' : ''}`}
                onClick={() => {
                  setIsRegistering(true);
                  resetForm();
                }}
              >
                Register
              </button>
            </div>

            {isRegistering ? renderRegisterForm() : renderLoginForm()}
          </section>
        </div>
      </div>
    </div>
  );
};

export default LoginComponent;
