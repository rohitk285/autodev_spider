// frontend/src/pages/Dashboard.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserId, clearAuthData } from '../services/authService';
import { fetchUserStories, selectStoryForAI } from '../services/storyService';
import './Dashboard.css';

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
  <article className="story-card">
    <header className="story-card-header">
      <h4 className="story-card-title">{story.title}</h4>
      <span className="story-card-azure-id">#{story.azure_id}</span>
    </header>

    <p className="story-card-description">{story.description}</p>

    <div className="story-card-footer">
      <button
        onClick={() => onSelect(story.id)}
        className="btn btn-primary story-select-btn"
      >
        Select for AI Processing
      </button>
    </div>
  </article>
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

        // If token/user is invalid mid-session, send back to login
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
    clearAuthData();
    navigate('/login');
  };

  // --- Render Logic ---
  if (!userId) {
    return null;
  }

  if (loading) {
    return (
      <div className="page-wrapper dashboard-page">
        <div className="dashboard-loading-card">
          <div className="dashboard-loading-spinner" />
          <p className="dashboard-loading-text">Loading your stories...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper dashboard-page">
      <div className="dashboard-inner">
        <header className="dashboard-header">
          <div className="dashboard-title-group">
            <h1 className="dashboard-title">AutoDev Spidey Dashboard</h1>
            <p className="dashboard-subtitle">
              Manage your assigned stories and trigger AI processing.
            </p>
          </div>

          <div className="dashboard-user-block">
            <span className="user-id-label">User</span>
            <span className="user-id-display">#{userId}</span>
            <button
              onClick={handleLogout}
              className="btn btn-outline logout-button"
            >
              Logout
            </button>
          </div>
        </header>

        {error && (
          <div className="alert alert--error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {aiMessage && (
          <div className="alert alert--info">
            <span>{aiMessage}</span>
          </div>
        )}

        <section className="story-section">
          <div className="story-section-header">
            <h2 className="story-section-title">Your Assigned Stories</h2>
            <p className="story-section-subtitle">
              Select a story to send it to the AI engine for processing.
            </p>
          </div>

          {stories.length > 0 ? (
            <div className="story-grid">
              {stories.map((story) => (
                <StoryCard
                  key={story.id}
                  story={story}
                  onSelect={handleStorySelection}
                />
              ))}
            </div>
          ) : (
            <p className="no-stories-message">
              No stories found for your user account.
            </p>
          )}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
