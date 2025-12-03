import React, { useState, useEffect } from 'react';
import { createProject, updateProject } from '../services/api';

const ProjectForm = ({ projectToEdit, onFormSubmit }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    technologies: '',
  });

  useEffect(() => {
    if (projectToEdit) {
      setFormData(projectToEdit);
    }
  }, [projectToEdit]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (projectToEdit) {
        await updateProject(projectToEdit.id, formData);
      } else {
        await createProject(formData);
      }
      onFormSubmit(); // Zgłoś sukces do komponentu nadrzędnego
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>{projectToEdit ? 'Edit Project' : 'Create Project'}</h2>
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
        <label>Description:</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label>Technologies:</label>
        <input
          type="text"
          name="technologies"
          value={formData.technologies}
          onChange={handleChange}
          required
        />
      </div>
      <button type="submit">{projectToEdit ? 'Update' : 'Create'}</button>
    </form>
  );
};

export default ProjectForm;
