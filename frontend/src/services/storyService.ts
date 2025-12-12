// frontend/src/services/storyService.ts

import axios from 'axios';
import { API_BASE_URL } from '../config';
import { getUserId, clearAuthData } from './authService';

const STORY_URL = `${API_BASE_URL}/story`;

// The structure we send to Dashboard after processing
export interface Story {
    id: number;          // generated on frontend
    azure_id: number;
    title: string;
    description: string;
}

interface BackendStoryGroupResponse {
    success: boolean;
    stories: {
        azure_id: number;
        title: string;
        description: string;
    }[];
}

// Fetch user stories from backend
export const fetchAllStoryGroups = async () => {
    const userId = getUserId();
    if (!userId) throw new Error("User ID missing");

    const response = await axios.get(`${STORY_URL}/retrievestory?userid=${userId}`);
    return response.data.groups;  // array of groups
};

// Send story to AI processing
export const selectStoryForAI = async (storyId: number) => {
    try {
        const response = await axios.post(`${STORY_URL}/${storyId}/select`);
        return response.data;
    } catch (error) {
        console.error("Failed to select story for AI:", error);

        if (axios.isAxiosError(error) && error.response) {
            throw new Error(error.response.data?.detail || "AI processing failed.");
        }

        throw new Error("Network error during AI selection.");
    }
};
