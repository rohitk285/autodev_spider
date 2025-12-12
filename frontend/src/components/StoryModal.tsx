import React from "react";
import "./StoryModal.css";

const StoryModal = ({ group, onClose }: any) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-box"
        onClick={(e) => e.stopPropagation()} // prevent closing when clicking inside
      >
        <h2>{group.app.toUpperCase()} — Story Points</h2>

        <div className="modal-content">
          {group.stories.map((story: any, idx: number) => (
            <div key={idx} className="modal-story-item">
              <h4>
                #{story.azure_id} — {story.title}
              </h4>
              <p>{story.description}</p>
            </div>
          ))}
        </div>

        <button className="btn btn-primary" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default StoryModal;
