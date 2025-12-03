const API_URL = 'http://localhost:8000/api'; // Załóżmy, że backend działa na porcie 8000
const API_KEY = 'super_secret_api_key'; // Klucz API do autoryzacji

// Funkcja pomocnicza do obsługi zapytań
const fetchApi = async (url, options = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (options.requiresAuth) {
    headers['X-API-Key'] = API_KEY;
  }

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Funkcja pomocnicza do przesyłania plików
const uploadFileApi = async (url, formData, options = {}) => {
    const headers = {
        ...options.headers,
    };

    if (options.requiresAuth) {
        headers['X-API-Key'] = API_KEY;
    }

    const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers,
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
}

// Funkcje API dla projektów
export const getProjects = () => fetchApi(`${API_URL}/projects/`);

export const createProject = (projectData) =>
  fetchApi(`${API_URL}/admin/projects/`, {
    method: 'POST',
    body: JSON.stringify(projectData),
    requiresAuth: true,
  });

export const updateProject = (projectId, projectData) =>
  fetchApi(`${API_URL}/admin/projects/${projectId}`, {
    method: 'PUT',
    body: JSON.stringify(projectData),
    requiresAuth: true,
  });

export const deleteProject = (projectId) =>
  fetchApi(`${API_URL}/admin/projects/${projectId}`, {
    method: 'DELETE',
    requiresAuth: true,
  });

// Funkcje API dla wydarzeń
export const getEvents = () => fetchApi(`${API_URL}/events/`);

export const createEvent = (eventData) =>
    fetchApi(`${API_URL}/admin/events/`, {
        method: 'POST',
        body: JSON.stringify(eventData),
        requiresAuth: true,
    });

export const updateEvent = (eventId, eventData) =>
    fetchApi(`${API_URL}/admin/events/${eventId}`, {
        method: 'PUT',
        body: JSON.stringify(eventData),
        requiresAuth: true,
    });

export const deleteEvent = (eventId) =>
    fetchApi(`${API_URL}/admin/events/${eventId}`, {
        method: 'DELETE',
        requiresAuth: true,
    });

// Funkcje API dla informacji o grupie
export const getGroupInfo = () => fetchApi(`${API_URL}/about/`);

export const createGroupInfo = (groupInfoData) =>
    fetchApi(`${API_URL}/admin/about/`, {
        method: 'POST',
        body: JSON.stringify(groupInfoData),
        requiresAuth: true,
    });

export const updateGroupInfo = (groupInfoData) =>
    fetchApi(`${API_URL}/admin/about/`, {
        method: 'PUT',
        body: JSON.stringify(groupInfoData),
        requiresAuth: true,
    });


// Funkcje API dla obrazów
export const uploadImage = (formData) =>
    uploadFileApi(`${API_URL}/admin/upload_image/`, formData, { requiresAuth: true });

export const getEventImages = (eventId) => fetchApi(`${API_URL}/gallery/event/${eventId}`);

export const getProjectImages = (projectId) => fetchApi(`${API_URL}/gallery/project/${projectId}`);

export const deleteImage = (imageId) =>
    fetchApi(`${API_URL}/admin/images/${imageId}`, {
        method: 'DELETE',
        requiresAuth: true,
    });
