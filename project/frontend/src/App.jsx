import React, { useEffect, useState } from 'react'
import api from './api'

function Todo({ item, onToggle, onDelete }) {
  return (
    <div className={`todo ${item.done ? 'done' : ''}`}>
      <label>
        <input type="checkbox" checked={item.done} onChange={() => onToggle(item.id, !item.done)} />
        <span>{item.title}</span>
      </label>
      <button className="delete" onClick={() => onDelete(item.id)}>X</button>
    </div>
  )
}

export default function App() {
  const [todos, setTodos] = useState([])
  const [title, setTitle] = useState('')

  useEffect(() => { load() }, [])

  async function load() {
    const res = await api.get('/todos')
    setTodos(res.data)
  }

  async function add(e) {
    e.preventDefault()
    if (!title.trim()) return
    const res = await api.post('/todos', { title })
    setTodos([res.data, ...todos])
    setTitle('')
  }

  async function toggle(id, done) {
    const res = await api.put(`/todos/${id}`, { done })
    setTodos(todos.map(t => t.id === id ? res.data : t))
  }

  async function remove(id) {
    await api.delete(`/todos/${id}`)
    setTodos(todos.filter(t => t.id !== id))
  }

  return (
    <div className="container">
      <h1>Todo App</h1>
      <form onSubmit={add} className="add-form">
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Add todo..." />
        <button>Add</button>
      </form>
      <div className="list">
        {todos.map(t => (
          <Todo key={t.id} item={t} onToggle={toggle} onDelete={remove} />
        ))}
      </div>
    </div>
  )
}
