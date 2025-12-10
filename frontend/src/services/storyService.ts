// frontend/src/services/storyService.ts

import axios from 'axios';
import { API_BASE_URL } from '../config'; 
import { getUserId, clearAuthData } from './authService';

const STORY_URL = `${API_BASE_URL}/story`;

// --- TYPE DEFINITIONS ---
interface Story {
    id: number;
    azure_id: string;
    title: string;
    description: string;
}

// Matches the backend response: {"success": "link hitting", "story": [...]}
interface StoryListResponse {
    success: string;
    story: Story[];
}

interface AIMessageResponse {
    message: string;
}

// --- API Call Functions ---

/**
 * Fetches the user's stories from the protected endpoint.
 * Authorization relies on the session cookie.
 */
export const fetchUserStories = async (): Promise<StoryListResponse> => {
    try {
        const userId = getUserId(); 
        
        if (!userId) {
            throw new Error("User ID missing. Authentication required.");
        }

        // --- CRUCIAL CHANGE: Construct the URL with the Query Parameter ---
        const requestUrl = `${STORY_URL}/retrievestory?userid=${userId}`;
        // ------------------------------------------------------------------

        // The request implicitly includes the session cookie due to global axios config
        const response = await axios.get<StoryListResponse>(requestUrl);

        return response.data;

    } catch (error) {
        console.error('Failed to fetch stories:', error);
        
        // Error handling for 401/403 remains important for session management
        if (axios.isAxiosError(error) && error.response && (error.response.status === 401 || error.response.status === 403)) {
            clearAuthData(); 
        }
        throw new Error("Could not load stories. Your session may have expired.");
    }
};

/**
 * Sends the selected story to the backend to initiate AI processing.
 */
export const selectStoryForAI = async (storyId: number): Promise<AIMessageResponse> => {
    try {
        // Example POST route: /api/stories/123/select
        const response = await axios.post<AIMessageResponse>(`${STORY_URL}/${storyId}/select`);
        return response.data;
    } catch (error) {
        console.error('Failed to select story for AI:', error);
        if (axios.isAxiosError(error) && error.response) {
            const detail = error.response.data?.detail || 'Failed to start AI processing.';
            throw new Error(detail);
        }
        throw new Error('Network error during AI selection.');
    }
};