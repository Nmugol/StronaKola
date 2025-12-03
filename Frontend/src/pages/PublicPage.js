import React, { useState, useEffect } from 'react';
import { getProjects, getEvents, getGroupInfo, getProjectImages, getEventImages } from '../services/api';

const PublicPage = () => {
  const [projects, setProjects] = useState([]);
  const [events, setEvents] = useState([]);
  const [groupInfo, setGroupInfo] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const projectsData = await getProjects();
      const eventsData = await getEvents();
      const groupInfoData = await getGroupInfo();
      
      // For each project and event, fetch their images
      for (const project of projectsData) {
        project.images = await getProjectImages(project.id);
      }
      for (const event of eventsData) {
        event.images = await getEventImages(event.id);
      }

      setProjects(projectsData);
      setEvents(eventsData);
      setGroupInfo(groupInfoData);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div>
      {groupInfo && (
        <section>
          <h1>About Us</h1>
          <p>{groupInfo.description}</p>
          <p>Contact: {groupInfo.contact}</p>
        </section>
      )}

      <hr/>

      <section>
        <h1>Projects</h1>
        {projects.map((project) => (
          <div key={project.id}>
            <h2>{project.name}</h2>
            <p>{project.description}</p>
            <p>
              <strong>Technologies:</strong> {project.technologies}
            </p>
            <div>
              {project.images && project.images.map(image => (
                <img key={image.id} src={`http://localhost:8000/${image.file_path}`} alt="" style={{width: '100px', margin: '5px'}} />
              ))}
            </div>
          </div>
        ))}
      </section>

      <hr/>

      <section>
        <h1>Events</h1>
        {events.map((event) => (
          <div key={event.id}>
            <h2>{event.name}</h2>
            <p>Date: {new Date(event.date).toLocaleDateString()}</p>
            <p>{event.description}</p>
            <div>
              {event.images && event.images.map(image => (
                <img key={image.id} src={`http://localhost:8000/${image.file_path}`} alt="" style={{width: '100px', margin: '5px'}} />
              ))}
            </div>
          </div>
        ))}
      </section>

    </div>
  );
};

export default PublicPage;
