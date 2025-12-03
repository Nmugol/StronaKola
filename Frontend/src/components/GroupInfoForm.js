import React, { useState, useEffect } from 'react';
import { getGroupInfo, updateGroupInfo, createGroupInfo } from '../services/api';

const GroupInfoForm = () => {
  const [formData, setFormData] = useState({
    description: '',
    contact: '',
  });
  const [exists, setExists] = useState(false);

  useEffect(() => {
    fetchGroupInfo();
  }, []);

  const fetchGroupInfo = async () => {
    try {
      const groupInfoData = await getGroupInfo();
      setFormData(groupInfoData);
      setExists(true);
    } catch (error) {
      console.error('Error fetching group info:', error);
      setExists(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (exists) {
        await updateGroupInfo(formData);
      } else {
        await createGroupInfo(formData);
      }
      fetchGroupInfo(); // Refresh data
      alert('Group info updated successfully!');
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Failed to update group info.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Manage Group Info</h2>
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
        <label>Contact:</label>
        <input
          type="text"
          name="contact"
          value={formData.contact}
          onChange={handleChange}
          required
        />
      </div>
      <button type="submit">{exists ? 'Update' : 'Create'}</button>
    </form>
  );
};

export default GroupInfoForm;
