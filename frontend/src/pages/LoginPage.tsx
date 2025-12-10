// frontend/src/pages/LoginPage.tsx (Updated for PoC Requirements)

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
// --- NEW: Import the authentication services ---
import { login, register } from '../services/authService'; 
// NOTE: Ensure your authService.ts is in place!

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
    const resetForm = () => {
        setUsername('');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
        setError(null);
        setMessage(null);
    };

    // --- Handlers ---

    const handleRegistrationSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setMessage(null);

        if (password !== confirmPassword) {
            return setError("Passwords do not match.");
        }

        try {
            // 1. CALL THE REGISTER SERVICE
            const newUser = await register(username, email, password, confirmPassword);
            
            setMessage(`Registration successful for ${newUser.username}! Please log in.`);
            setIsRegistering(false); // Switch to login form
            resetForm();

        } catch (err: any) {
            setError(err.message || 'Registration failed due to an unknown error.');
        }
    };

    const handleLoginSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setMessage(null);

        try {
            // 1. CALL THE LOGIN SERVICE
            const { userId } = await login(username, password);
            console.log(userId)
            // 2. Redirect on Success
            // Since login success means session cookie and local ID are set, redirect to dashboard.
            navigate('/dashboard'); 

        } catch (err: any) {
            // Display error from service/backend
            setError(err.message || 'Login failed. Check username and password.');
        }
    };

    // --- Render Forms ---

    const renderLoginForm = () => (
        <form className="login-form" onSubmit={handleLoginSubmit}>
            <h2>Sign In</h2>
            <input type="text" placeholder="Username or Email" value={username} onChange={(e) => setUsername(e.target.value)} required />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            
            {error && <p className="error-message" style={{ color: 'red' }}>{error}</p>}
            
            <button type="submit" className="login-submit-button">Log In</button>
            <p className="switch-link">
                Need an account? <a href="#" onClick={(e) => { e.preventDefault(); setIsRegistering(true); resetForm(); }}>Register here</a>
            </p>
        </form>
    );

    const renderRegisterForm = () => (
        <form className="register-form" onSubmit={handleRegistrationSubmit}>
            <h2>Sign Up</h2>
            <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <input type="password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
            
            {error && <p className="error-message" style={{ color: 'red' }}>{error}</p>}

            <button type="submit" className="register-submit-button">Sign Up</button>
            <p className="switch-link">
                Already have an account? <a href="#" onClick={(e) => { e.preventDefault(); setIsRegistering(false); resetForm(); }}>Login</a>
            </p>
        </form>
    );


    return (
        <div className="auth-container">
            <p className="back-link"><Link to="/">← Back to Home</Link></p>
            {message && <p style={{ color: 'green', fontWeight: 'bold' }}>{message}</p>}

            {isRegistering ? renderRegisterForm() : renderLoginForm()}
        </div>
    );
};

export default LoginComponent;