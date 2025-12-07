import React, { useState, useEffect } from "react";

const API_URL = "http://localhost:8000";

export default function AdminPage() {
  const [apiKey, setApiKey] = useState("tajny-klucz-api");

  // --- STANY ---
  const [projects, setProjects] = useState([]);
  const [events, setEvents] = useState([]);
  const [groupInfo, setGroupInfo] = useState({ description: "", contact: "" });

  // Czy info o grupie już istnieje w bazie? (do decydowania między POST a PUT)
  const [infoExists, setInfoExists] = useState(false);

  // Formularze
  const [newProject, setNewProject] = useState({
    name: "",
    description: "",
    technologies: "",
  });

  const [newEvent, setNewEvent] = useState({
    name: "",
    date: "",
    description: "",
  });

  useEffect(() => {
    refreshData();
  }, []);

  const refreshData = async () => {
    await Promise.all([fetchProjects(), fetchEvents(), fetchGroupInfo()]);
  };

  // --- FETCHERS ---
  const fetchProjects = async () => {
    try {
      const res = await fetch(`${API_URL}/api/projects/`);
      const data = await res.json();
      setProjects(data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchEvents = async () => {
    try {
      const res = await fetch(`${API_URL}/api/events/`);
      const data = await res.json();
      setEvents(data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchGroupInfo = async () => {
    try {
      const res = await fetch(`${API_URL}/api/about/`);
      if (res.ok) {
        const data = await res.json();
        setGroupInfo({ description: data.description, contact: data.contact });
        setInfoExists(true);
      } else {
        setInfoExists(false); // 404 oznacza, że jeszcze nie utworzono info
      }
    } catch (e) {
      console.error(e);
    }
  };

  // --- LOGIKA GRUPOWA (INFO) ---
  const handleSaveGroupInfo = async (e) => {
    e.preventDefault();
    // Jeśli info istnieje -> PUT, jeśli nie -> POST
    const method = infoExists ? "PUT" : "POST";
    const endpoint = "/api/admin/about/";

    const res = await fetch(`${API_URL}${endpoint}`, {
      method: method,
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
      },
      body: JSON.stringify(groupInfo),
    });

    if (res.ok) {
      alert("Informacje o grupie zapisane!");
      fetchGroupInfo();
    } else {
      alert("Błąd zapisu info: " + res.status);
    }
  };

  // --- LOGIKA EVENTÓW ---
  const handleCreateEvent = async (e) => {
    e.preventDefault();
    const res = await fetch(`${API_URL}/api/admin/events/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
      },
      body: JSON.stringify(newEvent),
    });

    if (res.ok) {
      alert("Wydarzenie dodane!");
      setNewEvent({ name: "", date: "", description: "" });
      fetchEvents();
    } else {
      alert("Błąd dodawania wydarzenia: " + res.status);
    }
  };

  const handleDeleteEvent = async (id) => {
    if (!window.confirm("Usunąć wydarzenie?")) return;
    await fetch(`${API_URL}/api/admin/events/${id}`, {
      method: "DELETE",
      headers: { "x-api-key": apiKey },
    });
    fetchEvents();
  };

  // --- LOGIKA PROJEKTÓW (istniejąca) ---
  const handleCreateProject = async (e) => {
    e.preventDefault();
    const res = await fetch(`${API_URL}/api/admin/projects/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
      },
      body: JSON.stringify(newProject),
    });
    if (res.ok) {
      alert("Projekt utworzony!");
      setNewProject({ name: "", description: "", technologies: "" });
      fetchProjects();
    } else {
      alert("Błąd tworzenia projektu: " + res.status);
    }
  };

  const handleDeleteProject = async (id) => {
    if (!window.confirm("Usunąć projekt?")) return;
    await fetch(`${API_URL}/api/admin/projects/${id}`, {
      method: "DELETE",
      headers: { "x-api-key": apiKey },
    });
    fetchProjects();
  };

  // --- LOGIKA UPLOADU PLIKÓW ---
  const uploadFile = async (endpoint, formData) => {
    const res = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: { "x-api-key": apiKey },
      body: formData,
    });
    if (res.ok) {
      alert("Plik przesłany!");
      refreshData();
    } else {
      const err = await res.json();
      alert("Błąd: " + JSON.stringify(err));
    }
  };

  const handleUploadProjectImage = (projectId, file) => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("project_id", projectId);
    uploadFile("/api/admin/upload_image/", fd);
  };

  const handleUploadEventImage = (eventId, file) => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("event_id", eventId); // Backend obsługuje event_id
    uploadFile("/api/admin/upload_image/", fd);
  };

  const handleUploadZip = (projectId, file) => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("project_id", projectId);
    uploadFile("/api/admin/projects/files/upload", fd);
  };

  const handleUploadExe = (projectId, file, version, platform) => {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("project_id", projectId);
    fd.append("version", version);
    fd.append("platform", platform);
    uploadFile("/api/admin/projects/executables/upload", fd);
  };

  return (
    <div
      style={{
        padding: 20,
        backgroundColor: "#f0f0f0",
        fontFamily: "sans-serif",
      }}
    >
      <h1>Panel Admina</h1>

      {/* KONFIGURACJA KLUCZA */}
      <div
        style={{
          marginBottom: 20,
          padding: 10,
          background: "#fff3cd",
          border: "1px solid #ffeeba",
        }}
      >
        <label>
          <strong>Twój API Key: </strong>
        </label>
        <input
          type="text"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          style={{ width: 300, marginLeft: 10 }}
        />
      </div>

      <hr />

      {/* --- SEKCJA 1: INFORMACJE O GRUPIE --- */}
      <div
        style={{
          border: "2px solid #28a745",
          padding: 15,
          marginBottom: 30,
          background: "white",
        }}
      >
        <h2 style={{ marginTop: 0, color: "#28a745" }}>
          1. Informacje o Grupie (About)
        </h2>
        <form onSubmit={handleSaveGroupInfo}>
          <div style={{ marginBottom: 10 }}>
            <label>Opis grupy:</label>
            <br />
            <textarea
              rows={3}
              style={{ width: "100%" }}
              value={groupInfo.description}
              onChange={(e) =>
                setGroupInfo({ ...groupInfo, description: e.target.value })
              }
            />
          </div>
          <div style={{ marginBottom: 10 }}>
            <label>Kontakt:</label>
            <br />
            <input
              type="text"
              style={{ width: "100%" }}
              value={groupInfo.contact}
              onChange={(e) =>
                setGroupInfo({ ...groupInfo, contact: e.target.value })
              }
            />
          </div>
          <button
            type="submit"
            style={{
              padding: "10px 20px",
              background: "#28a745",
              color: "white",
              border: "none",
              cursor: "pointer",
            }}
          >
            {infoExists ? "Zaktualizuj Informacje" : "Utwórz Informacje"}
          </button>
        </form>
      </div>

      {/* --- SEKCJA 2: WYDARZENIA --- */}
      <div
        style={{
          border: "2px solid #17a2b8",
          padding: 15,
          marginBottom: 30,
          background: "white",
        }}
      >
        <h2 style={{ marginTop: 0, color: "#17a2b8" }}>
          2. Wydarzenia (Events)
        </h2>

        {/* Formularz dodawania eventu */}
        <div style={{ background: "#e9ecef", padding: 10, marginBottom: 15 }}>
          <h4>Dodaj nowe wydarzenie</h4>
          <form onSubmit={handleCreateEvent}>
            <input
              placeholder="Nazwa wydarzenia"
              value={newEvent.name}
              onChange={(e) =>
                setNewEvent({ ...newEvent, name: e.target.value })
              }
              required
              style={{ marginRight: 5 }}
            />
            <input
              type="datetime-local"
              value={newEvent.date}
              onChange={(e) =>
                setNewEvent({ ...newEvent, date: e.target.value })
              }
              required
              style={{ marginRight: 5 }}
            />
            <input
              placeholder="Krótki opis"
              value={newEvent.description}
              onChange={(e) =>
                setNewEvent({ ...newEvent, description: e.target.value })
              }
              required
              style={{ width: 300, marginRight: 5 }}
            />
            <button type="submit">Dodaj Event</button>
          </form>
        </div>

        {/* Lista eventów */}
        <div>
          {events.map((evt) => (
            <div
              key={evt.id}
              style={{
                borderBottom: "1px solid #ccc",
                padding: 10,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <strong>{evt.name}</strong>{" "}
                <small>({new Date(evt.date).toLocaleString()})</small>
                <p style={{ margin: "5px 0" }}>{evt.description}</p>
                {/* Miniaturki zdjęć */}
                <div>
                  {evt.images &&
                    evt.images.map((img) => (
                      <img
                        key={img.id}
                        src={`${API_URL}/${img.file_path}`}
                        alt="evt"
                        width="50"
                        style={{ marginRight: 5, border: "1px solid gray" }}
                      />
                    ))}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <button
                  onClick={() => handleDeleteEvent(evt.id)}
                  style={{ color: "red", marginBottom: 5 }}
                >
                  Usuń
                </button>
                <br />
                {/* Upload zdjęcia do eventu */}
                <label
                  style={{
                    fontSize: "0.8em",
                    cursor: "pointer",
                    background: "#eee",
                    padding: 2,
                  }}
                >
                  [+ Dodaj foto]
                  <input
                    type="file"
                    style={{ display: "none" }}
                    onChange={(e) => {
                      if (e.target.files[0])
                        handleUploadEventImage(evt.id, e.target.files[0]);
                    }}
                  />
                </label>
              </div>
            </div>
          ))}
          {events.length === 0 && <p>Brak wydarzeń.</p>}
        </div>
      </div>

      {/* --- SEKCJA 3: PROJEKTY --- */}
      <div
        style={{
          border: "2px solid #007bff",
          padding: 15,
          background: "white",
        }}
      >
        <h2 style={{ marginTop: 0, color: "#007bff" }}>
          3. Projekty (Projects)
        </h2>

        {/* Formularz projektu */}
        <div style={{ background: "#e9ecef", padding: 10, marginBottom: 15 }}>
          <h4>Dodaj nowy projekt</h4>
          <form onSubmit={handleCreateProject}>
            <input
              placeholder="Nazwa"
              value={newProject.name}
              onChange={(e) =>
                setNewProject({ ...newProject, name: e.target.value })
              }
              required
              style={{ marginRight: 5 }}
            />
            <input
              placeholder="Technologie"
              value={newProject.technologies}
              onChange={(e) =>
                setNewProject({ ...newProject, technologies: e.target.value })
              }
              required
              style={{ marginRight: 5 }}
            />
            <input
              placeholder="Opis"
              value={newProject.description}
              onChange={(e) =>
                setNewProject({ ...newProject, description: e.target.value })
              }
              required
              style={{ width: 300, marginRight: 5 }}
            />
            <button type="submit">Utwórz Projekt</button>
          </form>
        </div>

        {/* Lista projektów */}
        {projects.map((proj) => (
          <div
            key={proj.id}
            style={{
              border: "1px solid black",
              margin: "10px 0",
              padding: 10,
              background: "white",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <h4>
                ID: {proj.id} | {proj.name}
              </h4>
              <button
                onClick={() => handleDeleteProject(proj.id)}
                style={{ color: "red" }}
              >
                Usuń Projekt
              </button>
            </div>

            <p>
              <strong>Tech:</strong> {proj.technologies}
            </p>
            <p>{proj.description}</p>

            <div
              style={{
                display: "flex",
                gap: 15,
                marginTop: 10,
                background: "#f8f9fa",
                padding: 10,
              }}
            >
              {/* UPLOAD ZDJĘCIA */}
              <div style={{ borderRight: "1px solid #ddd", paddingRight: 15 }}>
                <p
                  style={{
                    margin: "0 0 5px 0",
                    fontWeight: "bold",
                    fontSize: "0.9em",
                  }}
                >
                  Zdjęcia ({proj.images.length})
                </p>
                <input
                  type="file"
                  onChange={(e) => {
                    if (e.target.files[0])
                      handleUploadProjectImage(proj.id, e.target.files[0]);
                  }}
                />
              </div>

              {/* UPLOAD ZIP */}
              <div style={{ borderRight: "1px solid #ddd", paddingRight: 15 }}>
                <p
                  style={{
                    margin: "0 0 5px 0",
                    fontWeight: "bold",
                    fontSize: "0.9em",
                  }}
                >
                  Kod ZIP ({proj.files.length})
                </p>
                <input
                  type="file"
                  onChange={(e) => {
                    if (e.target.files[0])
                      handleUploadZip(proj.id, e.target.files[0]);
                  }}
                />
              </div>

              {/* UPLOAD EXE */}
              <div>
                <p
                  style={{
                    margin: "0 0 5px 0",
                    fontWeight: "bold",
                    fontSize: "0.9em",
                  }}
                >
                  Plik EXE ({proj.executable.length})
                </p>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    const file = e.target.elements.exeFile.files[0];
                    const ver = e.target.elements.ver.value;
                    const plat = e.target.elements.plat.value;
                    if (file) handleUploadExe(proj.id, file, ver, plat);
                  }}
                  style={{ display: "flex", flexDirection: "column", gap: 3 }}
                >
                  <input type="file" name="exeFile" required />
                  <div style={{ display: "flex", gap: 5 }}>
                    <input
                      type="text"
                      name="ver"
                      placeholder="Ver 1.0"
                      required
                      size="6"
                    />
                    <select name="plat">
                      <option value="Windows">Windows</option>
                      <option value="Linux">Linux</option>
                      <option value="MacOS">MacOS</option>
                    </select>
                  </div>
                  <button type="submit" style={{ marginTop: 3 }}>
                    Wyślij EXE
                  </button>
                </form>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
