import React, { useState, useEffect } from 'react';
import { uploadImage, getProjects, getEvents } from '../services/api';

const ImageUploadForm = ({ onUpload }) => {
  const [file, setFile] = useState(null);
  const [projects, setProjects] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [selectedEventId, setSelectedEventId] = useState('');

  useEffect(() => {
    fetchProjectsAndEvents();
  }, []);

  const fetchProjectsAndEvents = async () => {
    try {
      const projectsData = await getProjects();
      const eventsData = await getEvents();
      setProjects(projectsData);
      setEvents(eventsData);
    } catch (error) {
      console.error('Error fetching projects and events:', error);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || (!selectedProjectId && !selectedEventId)) {
      alert('Please select a file and a project or event.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    if (selectedProjectId) {
      formData.append('project_id', selectedProjectId);
    } else if (selectedEventId) {
      formData.append('event_id', selectedEventId);
    }

    try {
      await uploadImage(formData);
      alert('Image uploaded successfully!');
      onUpload();
    } catch (error) {
      console.error('Error uploading image:', error);
      alert('Failed to upload image.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Upload Image</h2>
      <div>
        <label>Image:</label>
        <input type="file" onChange={handleFileChange} required />
      </div>
      <div>
        <label>Project:</label>
        <select
          value={selectedProjectId}
          onChange={(e) => {
            setSelectedProjectId(e.target.value);
            setSelectedEventId('');
          }}
        >
          <option value="">Select a project</option>
          {projects.map((project) => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label>Event:</label>
        <select
          value={selectedEventId}
          onChange={(e) => {
            setSelectedEventId(e.target.value);
            setSelectedProjectId('');
          }}
        >
          <option value="">Select an event</option>
          {events.map((event) => (
            <option key={event.id} value={event.id}>
              {event.name}
            </option>
          ))}
        </select>
      </div>
      <button type="submit">Upload</button>
    </form>
  );
};

export default ImageUploadForm;
