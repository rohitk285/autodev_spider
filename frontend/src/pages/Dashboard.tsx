// frontend/src/pages/Dashboard.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
// Import services and helpers
import { getUserId, clearAuthData } from '../services/authService';
import { fetchUserStories, selectStoryForAI } from '../services/storyService';

// Define the structure for a single story item
interface Story {
    id: number;
    azure_id: string;
    title: string;
    description: string;
}

// --- Component for a Single Story Card ---
interface StoryCardProps {
    story: Story;
    onSelect: (storyId: number) => void;
}

const StoryCard: React.FC<StoryCardProps> = ({ story, onSelect }) => (
    <div style={styles.card}>
        <h4 style={styles.cardTitle}>{story.title} <span style={styles.azureId}>({story.azure_id})</span></h4>
        <p>{story.description}</p>
        <button 
            onClick={() => onSelect(story.id)}
            style={styles.selectButton}
        >
            Select for AI Processing
        </button>
    </div>
);


const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const userId = getUserId();
    const [stories, setStories] = useState<Story[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [aiMessage, setAiMessage] = useState<string | null>(null);

    // --- Data Fetching Effect ---
    useEffect(() => {
        if (!userId) {
            // Should be caught by the router, but serves as a failsafe
            navigate('/login');
            return;
        }

        const loadStories = async () => {
            try {
                setLoading(true);
                const storyData = await fetchUserStories();
                setStories(storyData.story);
                setError(null);
            } catch (err: any) {
                console.error('Error fetching stories:', err);
                // If service cleared auth data (due to 401), navigate to login
                if (!getUserId()) {
                     navigate('/login');
                     return;
                }
                setError(err.message || 'Failed to load stories.');
            } finally {
                setLoading(false);
            }
        };

        loadStories();
    }, [userId, navigate]);

    // --- AI Selection Handler ---
    const handleStorySelection = async (storyId: number) => {
        setAiMessage(null);
        try {
            setAiMessage(`Sending Story ID ${storyId} for AI processing...`);
            const response = await selectStoryForAI(storyId);
            setAiMessage(`AI processing started successfully: ${response.message}`);
        } catch (err: any) {
            setAiMessage(`Failed to start AI processing: ${err.message}`);
        }
    };

    // --- Logout Handler ---
    const handleLogout = () => {
        // Clear local storage (cookie remains in browser until expiration or backend logout route is hit)
        clearAuthData();
        // Redirect to login page
        navigate('/login');
    };

    // --- Render Logic ---
    if (!userId) {
        // Should be caught by useEffect, but render nothing briefly
        return null;
    }
    
    if (loading) {
        return <div style={styles.container}>Loading User Stories...</div>;
    }

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <h2>Dashboard: User {userId}</h2>
                <button onClick={handleLogout} style={styles.logoutButton}>
                    Logout
                </button>
            </div>

            {error && <p style={styles.error}>Error: {error}</p>}
            {aiMessage && <p style={styles.message}>{aiMessage}</p>}

            <h3 style={styles.storyHeader}>Your Assigned Stories:</h3>
            
            {stories.length > 0 ? (
                <div style={styles.storyGrid}>
                    {stories.map(story => (
                        <StoryCard 
                            key={story.id} 
                            story={story} 
                            onSelect={handleStorySelection}
                        />
                    ))}
                </div>
            ) : (
                <p>No stories found for your user account.</p>
            )}
        </div>
    );
};

// Simple inline styles for PoC clarity
const styles = {
    container: {
        maxWidth: '1000px',
        margin: '20px auto',
        padding: '20px',
        fontFamily: 'Arial, sans-serif',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        borderBottom: '2px solid #eee',
        paddingBottom: '10px',
        marginBottom: '20px',
    },
    logoutButton: {
        padding: '8px 15px',
        cursor: 'pointer',
        backgroundColor: '#dc3545',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
    },
    storyHeader: {
        marginTop: '30px',
        borderLeft: '4px solid #007bff',
        paddingLeft: '10px',
    },
    storyGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '20px',
    },
    card: {
        border: '1px solid #ddd',
        padding: '15px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
        backgroundColor: '#fff',
    },
    cardTitle: {
        marginTop: '0',
        marginBottom: '10px',
        color: '#007bff',
    },
    azureId: {
        fontSize: '0.9em',
        color: '#6c757d',
        fontWeight: 'normal',
    },
    selectButton: {
        marginTop: '15px',
        padding: '10px',
        backgroundColor: '#28a745',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        width: '100%',
    },
    error: {
        color: 'red',
        fontWeight: 'bold',
        padding: '10px',
        backgroundColor: '#f8d7da',
        border: '1px solid #f5c6cb',
        borderRadius: '5px',
    },
    message: {
        color: 'blue',
        padding: '10px',
        backgroundColor: '#d4edda',
        border: '1px solid #c3e6cb',
        borderRadius: '5px',
    }
};

export default Dashboard;