import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getUserId, clearAuthData } from "../services/authService";
import { fetchAllStoryGroups, selectStoryForAI } from "../services/storyService";
import "./Dashboard.css";
import StoryModal from "../components/StoryModal";

interface Story {
  azure_id: number;
  title: string;
  description: string;
}

interface StoryGroup {
  id: number;
  app: string;
  stories: Story[];
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const userId = getUserId();

  const [groups, setGroups] = useState<StoryGroup[]>([]);
  const [visibleGroups, setVisibleGroups] = useState<StoryGroup[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [aiMessage, setAiMessage] = useState<string | null>(null);

  const [mode, setMode] = useState<"azure" | "custom">("azure");
  const [customPrompt, setCustomPrompt] = useState("");

  const [modalGroup, setModalGroup] = useState<StoryGroup | null>(null); // NEW STATE

  useEffect(() => {
    if (!userId) {
      navigate("/login");
      return;
    }

    const loadGroups = async () => {
      try {
        setLoading(true);
        const data = await fetchAllStoryGroups();
        setGroups(data);
        setVisibleGroups(data.slice(0, 5));
      } catch (err: any) {
        setError(err.message || "Failed to load stories.");
      } finally {
        setLoading(false);
      }
    };

    loadGroups();
  }, [userId, navigate]);

  /* -------- SEARCH ONLY BY APP NAME -------- */
  const searchStories = (query: string) => {
    setSearchQuery(query);
    if (!query.trim()) {
      setVisibleGroups(groups.slice(0, 5));
      return;
    }
    const filtered = groups.filter((g) =>
      g.app.toLowerCase().includes(query.toLowerCase())
    );
    setVisibleGroups(filtered.slice(0, 5));
  };

  const showMore = () => {
    const count = visibleGroups.length;
    setVisibleGroups(groups.slice(0, count + 5));
  };

  const handleStorySelection = async (azureId: number) => {
    setAiMessage(`Sending story #${azureId} to AI...`);
    try {
      const res = await selectStoryForAI(azureId);
      setAiMessage(`AI processing started: ${res.message}`);
    } catch (err: any) {
      setAiMessage(`Error: ${err.message}`);
    }
  };

  const handleLogout = () => {
    clearAuthData();
    navigate("/login");
  };

  const handleCustomPromptSubmit = () => {
    if (!customPrompt.trim()) {
      setAiMessage("Please enter a prompt.");
      return;
    }
    setAiMessage("Processing your custom prompt...");
  };

  if (loading) {
    return (
      <div className="page-wrapper dashboard-page">
        <div className="dashboard-loading-card">
          <div className="dashboard-loading-spinner" />
          <p>Loading your stories...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper dashboard-page">
      <div className="dashboard-inner">
        {/* Header */}
        <header className="dashboard-header">
          <div className="dashboard-title-group">
            <h1>AutoDev Spidey Dashboard</h1>
            <p>Build applications from Azure DevOps stories or custom prompts.</p>
          </div>

          <div className="dashboard-user-block">
            <span>User</span>
            <span className="user-id-display">#{userId}</span>
            <button onClick={handleLogout} className="btn btn-outline">
              Logout
            </button>
          </div>
        </header>

        {/* Toggle */}
        <div className="toggle-container">
          <button
            className={`toggle-btn ${mode === "azure" ? "active" : ""}`}
            onClick={() => setMode("azure")}
          >
            Azure DevOps Stories
          </button>

          <button
            className={`toggle-btn ${mode === "custom" ? "active" : ""}`}
            onClick={() => setMode("custom")}
          >
            Custom Prompt
          </button>
        </div>

        {error && <div className="alert alert--error">{error}</div>}
        {aiMessage && <div className="alert alert--info">{aiMessage}</div>}

        {/* ------------------ Azure DevOps Mode ------------------ */}
        {mode === "azure" && (
          <section className="story-section">
            {/* Search Bar */}
            <input
              type="text"
              className="story-search-bar"
              placeholder="Search by app name..."
              value={searchQuery}
              onChange={(e) => searchStories(e.target.value)}
            />

            <div className="story-section-header">
              <h2>Your Story Groups</h2>
            </div>

            {visibleGroups.length === 0 ? (
              <p>No apps found.</p>
            ) : (
              <div className="story-grid">
                {visibleGroups.map((group) => (
                  <div
                    key={group.id}
                    className="story-card"
                    onClick={() => setModalGroup(group)} // OPEN MODAL
                    style={{ cursor: "pointer" }}
                  >
                    <header className="story-card-header">
                      <div>
                        <h4>{group.app.toUpperCase()}</h4>
                        <span>{group.stories.length} story points</span>
                      </div>

                      <button
                        className="btn btn-primary"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (group.stories.length > 0)
                            handleStorySelection(group.stories[0].azure_id);
                        }}
                      >
                        Create Application
                      </button>
                    </header>
                  </div>
                ))}
              </div>
            )}

            {visibleGroups.length < groups.length && (
              <button className="btn btn-outline load-more-btn" onClick={showMore}>
                Show More
              </button>
            )}
          </section>
        )}

        {/* ------------------ Custom Prompt Mode ------------------ */}
        {mode === "custom" && (
          <section className="story-section">
            <div className="story-section-header">
              <h2>Custom Prompt</h2>
            </div>

            <textarea
              className="custom-textarea"
              placeholder="Enter your application idea..."
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              rows={8}
            />

            <button
              className="btn btn-primary custom-submit-btn"
              onClick={handleCustomPromptSubmit}
            >
              Create Application
            </button>
          </section>
        )}
      </div>

      {/* ================== MODAL ================== */}
      {modalGroup && (
        <StoryModal group={modalGroup} onClose={() => setModalGroup(null)} />
      )}
    </div>
  );
};

export default Dashboard;
