import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [diaries, setDiaries] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [editId, setEditId] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL;

  useEffect(() => {
    fetchDiaries();
  }, []);

  const fetchDiaries = async () => {
    try {
      const response = await axios.get(`${API_URL}/diaries`);
      setDiaries(response.data);
    } catch (error) {
      console.error('Error fetching diaries', error);
    }
  };

  const handleCreateDiary = async () => {
    try {
      await axios.post(`${API_URL}/diaries`, { title, content });
      setTitle('');
      setContent('');
      fetchDiaries();
    } catch (error) {
      console.error('Error creating diary', error);
    }
  };

  const handleUpdateDiary = async () => {
    try {
      await axios.put(`${API_URL}/diaries/${editId}`, { title, content });
      setTitle('');
      setContent('');
      setEditId(null);
      fetchDiaries();
    } catch (error) {
      console.error('Error updating diary', error);
    }
  };

  const handleDeleteDiary = async (id) => {
    try {
      await axios.delete(`${API_URL}/diaries/${id}`);
      fetchDiaries();
    } catch (error) {
      console.error('Error deleting diary', error);
    }
  };

  const handleEditDiary = (diary) => {
    setTitle(diary.title);
    setContent(diary.content);
    setEditId(diary.id);
  };

  return (
    <div>
      <h1>Diary App</h1>
      <div>
        <input
          type="text"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          placeholder="Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        {editId ? (
          <button onClick={handleUpdateDiary}>Update Diary</button>
        ) : (
          <button onClick={handleCreateDiary}>Create Diary</button>
        )}
      </div>
      <div>
        <h2>Diaries</h2>
        <ul>
          {diaries.map(diary => (
            <li key={diary.id}>
              <h3>{diary.title}</h3>
              <p>{diary.content}</p>
              <button onClick={() => handleEditDiary(diary)}>Edit</button>
              <button onClick={() => handleDeleteDiary(diary.id)}>Delete</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
