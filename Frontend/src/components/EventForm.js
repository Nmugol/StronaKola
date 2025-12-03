import React, { useState, useEffect } from 'react';
import { createEvent, updateEvent } from '../services/api';

const EventForm = ({ eventToEdit, onFormSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    date: '',
    description: '',
  });

  useEffect(() => {
    if (eventToEdit) {
      // Format date for input field
      const formattedDate = new Date(eventToEdit.date).toISOString().split('T')[0];
      setFormData({ ...eventToEdit, date: formattedDate });
    }
  }, [eventToEdit]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (eventToEdit) {
        await updateEvent(eventToEdit.id, formData);
      } else {
        await createEvent(formData);
      }
      onFormSubmit();
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>{eventToEdit ? 'Edit Event' : 'Create Event'}</h2>
      <div>
        <label>Name:</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label>Date:</label>
        <input
          type="date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label>Description:</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          required
        />
      </div>
      <button type="submit">{eventToEdit ? 'Update' : 'Create'}</button>
    </form>
  );
};

export default EventForm;
