import React, { useState, useEffect } from 'react';
import * as api from './api';

function App() {
  const [tasks, setTasks] = useState([]);
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getAllTasks();
      setTasks(response.data);
    } catch (err) {
      console.error('Error fetching tasks:', err);
      setError('Failed to fetch tasks. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTaskDescription.trim()) return;

    try {
      const response = await api.createTask({ description: newTaskDescription });
      setTasks([...tasks, response.data]);
      setNewTaskDescription('');
    } catch (err) {
      console.error('Error adding task:', err);
      setError('Failed to add task. Please try again.');
    }
  };

  const handleToggleComplete = async (id, currentCompletedStatus) => {
    try {
      const response = await api.updateTask(id, { completed: !currentCompletedStatus });
      setTasks(tasks.map((task) => (task.id === id ? response.data : task)));
    } catch (err) {
      console.error('Error updating task:', err);
      setError('Failed to update task. Please try again.');
    }
  };

  const handleDeleteTask = async (id) => {
    try {
      await api.deleteTask(id);
      setTasks(tasks.filter((task) => task.id !== id));
    } catch (err) {
      console.error('Error deleting task:', err);
      setError('Failed to delete task. Please try again.');
    }
  };

  if (loading) {
    return <div className="container">Loading tasks...</div>;
  }

  if (error) {
    return <div className="container error-message">Error: {error}</div>;
  }

  return (
    <div className="container">
      <h1>To-Do List</h1>

      <form onSubmit={handleAddTask} className="add-task-form">
        <input
          type="text"
          value={newTaskDescription}
          onChange={(e) => setNewTaskDescription(e.target.value)}
          placeholder="Add a new task..."
          aria-label="New task description"
        />
        <button type="submit">Add Task</button>
      </form>

      {tasks.length === 0 ? (
        <p className="no-tasks-message">No tasks yet! Add one above.</p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li key={task.id} className={`task-item ${task.completed ? 'completed' : ''}`}>
              <input
                type="checkbox"
                checked={task.completed}
                onChange={() => handleToggleComplete(task.id, task.completed)}
                aria-label={`Mark "${task.description}" as ${task.completed ? 'incomplete' : 'complete'}`}
              />
              <span className="task-description">{task.description}</span>
              <button onClick={() => handleDeleteTask(task.id)} className="delete-button" aria-label={`Delete task "${task.description}"`}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
