import React, { useState, useEffect } from 'react';
import ProjectsList from '../components/ProjectsList';
import ProjectForm from '../components/ProjectForm';
import EventsList from '../components/EventsList';
import EventForm from '../components/EventForm';
import GroupInfoForm from '../components/GroupInfoForm';
import ImageUploadForm from '../components/ImageUploadForm';
import ImagesList from '../components/ImagesList';
import { getProjects, getEvents } from '../services/api';


const AdminPage = () => {
    const [currentView, setCurrentView] = useState('projects'); // projects, events, group-info, images

    const renderContent = () => {
        switch (currentView) {
            case 'projects':
                return <ProjectsAdmin />;
            case 'events':
                return <EventsAdmin />;
            case 'group-info':
                return <GroupInfoForm />;
            case 'images':
                return <ImagesAdmin />;
            default:
                return <ProjectsAdmin />;
        }
    }

    return (
        <div>
            <h1>Admin Panel</h1>
            <nav>
                <button onClick={() => setCurrentView('projects')}>Projects</button>
                <button onClick={() => setCurrentView('events')}>Events</button>
                <button onClick={() => setCurrentView('group-info')}>Group Info</button>
                <button onClick={() => setCurrentView('images')}>Images</button>
            </nav>
            <hr />
            {renderContent()}
        </div>
    );
};

// Wrapper for project administration
const ProjectsAdmin = () => {
    const [editingProject, setEditingProject] = useState(null);
    const [showForm, setShowForm] = useState(false);

    const handleEdit = (project) => {
        setEditingProject(project);
        setShowForm(true);
    };

    const handleCreate = () => {
        setEditingProject(null);
        setShowForm(true);
    };

    const handleFormSubmit = () => {
        setShowForm(false);
        // ProjectsList will refetch automatically
    };

    return (
        <div>
            {showForm ? (
                <ProjectForm
                    projectToEdit={editingProject}
                    onFormSubmit={handleFormSubmit}
                />
            ) : (
                <>
                    <button onClick={handleCreate}>Create New Project</button>
                    <ProjectsList onEdit={handleEdit} />
                </>
            )}
        </div>
    );
}

// Wrapper for event administration
const EventsAdmin = () => {
    const [editingEvent, setEditingEvent] = useState(null);
    const [showForm, setShowForm] = useState(false);

    const handleEdit = (event) => {
        setEditingEvent(event);
        setShowForm(true);
    };

    const handleCreate = () => {
        setEditingEvent(null);
        setShowForm(true);
    };

    const handleFormSubmit = () => {
        setShowForm(false);
        // EventsList will refetch automatically
    };

    return (
        <div>
            {showForm ? (
                <EventForm
                    eventToEdit={editingEvent}
                    onFormSubmit={handleFormSubmit}
                />
            ) : (
                <>
                    <button onClick={handleCreate}>Create New Event</button>
                    <EventsList onEdit={handleEdit} />
                </>
            )}
        </div>
    );
}

// Wrapper for image administration
const ImagesAdmin = () => {
    const [projects, setProjects] = useState([]);
    const [events, setEvents] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState('');
    const [selectedEventId, setSelectedEventId] = useState('');
    const [refresh, setRefresh] = useState(0);

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

    const handleUpload = () => {
        setRefresh(refresh + 1);
    }

    return (
        <div>
            <h2>Manage Images</h2>
            <ImageUploadForm onUpload={handleUpload} />
            <hr />
            <h3>View Images</h3>
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
            <ImagesList projectId={selectedProjectId} eventId={selectedEventId} key={refresh} />
        </div>
    );
}

export default AdminPage;
