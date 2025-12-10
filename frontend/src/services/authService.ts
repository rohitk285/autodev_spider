import axios from 'axios';
// NOTE: Ensure your config.ts file exists and exports API_BASE_URL
import { API_BASE_URL } from '../config'; 

// --- TYPE DEFINITIONS ---

// Structure for the response after a successful registration (User object)
interface UserResponse {
    id: number;
    username: string;
    email: string;
}

// Structure for the response after a successful login (Simplified PoC response)
interface LoginResponse {
    user_id: number;
    message?: string;
}

// --- CONSTANTS ---
const AUTH_URL = `${API_BASE_URL}/auth`;
const USER_ID_KEY = 'autodev_user_id'; 

// --- Global Axios Configuration: CRITICAL for session cookies ---
// This tells the browser to include the session cookie sent by the backend.
axios.defaults.withCredentials = true;

// --- Local Storage Management ---

export const setUserId = (userId: number): void => {
    // Store the user's ID locally 
    localStorage.setItem(USER_ID_KEY, userId.toString());
};

export const clearAuthData = (): void => {
    // Clear the local ID when logging out.
    localStorage.removeItem(USER_ID_KEY); 
    // The browser handles the session cookie destruction upon backend logout or expiration.
};

export const getUserId = (): number | null => {
    const userIdStr = localStorage.getItem(USER_ID_KEY);
    // Return the ID as a number, or null if not found
    return userIdStr ? parseInt(userIdStr, 10) : null;
};


// --- API Call Functions ---

/**
 * Handles the Sign-up process (POST /api/auth/register).
 * Includes client-side password matching.
 */
export const register = async (
    username: string, 
    email: string, 
    password: string, 
    confirmPassword: string
): Promise<UserResponse> => {
    
    // 1. Client-side Validation
    if (password !== confirmPassword) {
        throw new Error("Passwords do not match.");
    }

    try {
        // Backend expects a JSON body
        const response = await axios.post<UserResponse>(`${AUTH_URL}/register`, {
            username,
            email,
            password,
        });
        
        return response.data; 

    } catch (error) {
        console.error('Registration failed:', error);
        if (axios.isAxiosError(error) && error.response) {
            // Extract the specific error detail from the FastAPI response body
            const detail = error.response.data?.detail || 'Registration failed due to server error.';
            throw new Error(detail);
        }
        throw new Error('An unknown network error occurred during registration.');
    }
};


/**
 * Handles the Login process (POST /api/auth/token).
 * Backend sets the session cookie and returns the user_id.
 */
export const login = async (username: string, password: string): Promise<{ userId: number }> => {
    
    // 1. Prepare Data: The /signin endpoint requires 'application/x-www-form-urlencoded' form data.
    const loginPayload = {
        username: username, // Matches UserSignin Pydantic field
        password: password  // Matches UserSignin Pydantic field
    };

    try {
        // --- CHANGE 1: Update endpoint from /token to /signin ---
        const response = await axios.post<LoginResponse>(`${AUTH_URL}/signin`, loginPayload);

        // 2. Process Response: Destructure the expected 'user_id'
        const { user_id } = response.data; 
        
        if (!user_id) {
            throw new Error("Login successful, but user ID was not returned by the server.");
        }
        
        // 3. Store ID: Save the user ID locally 
        setUserId(user_id);
        
        return { userId: user_id };

    } catch (error) {
        console.error('Login failed:', error);
        if (axios.isAxiosError(error) && error.response) {
            // Extract the specific error detail from the FastAPI response body
            // If the backend returns a JSON error like {"failed": "incorrect username or password"}
            const detail = error.response.data?.failed || error.response.data?.detail || 'Login failed.';
            throw new Error(detail);
        }
        throw new Error('An unknown network error occurred during login.');
    }
};