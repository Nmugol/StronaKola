import React, { useState, useEffect } from 'react';
import { getProjectImages, getEventImages, deleteImage } from '../services/api';

const ImagesList = ({ projectId, eventId }) => {
  const [images, setImages] = useState([]);

  useEffect(() => {
    fetchImages();
  }, [projectId, eventId]);

  const fetchImages = async () => {
    if (!projectId && !eventId) {
      setImages([]);
      return;
    }

    try {
      const imagesData = projectId
        ? await getProjectImages(projectId)
        : await getEventImages(eventId);
      setImages(imagesData);
    } catch (error) {
      console.error('Error fetching images:', error);
    }
  };

  const handleDelete = async (imageId) => {
    if (window.confirm('Are you sure you want to delete this image?')) {
      try {
        await deleteImage(imageId);
        fetchImages();
      } catch (error) {
        console.error('Error deleting image:', error);
      }
    }
  };

  return (
    <div>
      <h3>Images</h3>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
        {images.map((image) => (
          <div key={image.id} style={{ margin: '10px' }}>
            <img
              src={`http://localhost:8000/${image.file_path}`}
              alt=""
              style={{ width: '200px', height: 'auto' }}
            />
            <button onClick={() => handleDelete(image.id)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ImagesList;
