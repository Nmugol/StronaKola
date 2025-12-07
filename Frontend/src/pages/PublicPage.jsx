import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:8000";

export default function PublicPage() {
  const [projects, setProjects] = useState([]);
  const [events, setEvents] = useState([]);
  const [groupInfo, setGroupInfo] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Pobieranie projektów
      const resProj = await fetch(`${API_URL}/api/projects/`);
      const dataProj = await resProj.json();
      setProjects(dataProj);

      // Pobieranie eventów
      const resEvent = await fetch(`${API_URL}/api/events/`);
      const dataEvent = await resEvent.json();
      setEvents(dataEvent);

      // Pobieranie info
      const resInfo = await fetch(`${API_URL}/api/about/`);
      if (resInfo.ok) {
        const dataInfo = await resInfo.json();
        setGroupInfo(dataInfo);
      }
    } catch (err) {
      console.error("Błąd pobierania danych", err);
    }
  };

  // Helper do wyświetlania obrazków
  const getImageUrl = (path) => {
    // Backend zwraca np. "static/images/foto.jpg", musimy dodać host
    return `${API_URL}/${path}`;
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Strona Publiczna</h1>

      {/* SEKCJA O NAS */}
      <section
        style={{ border: "1px solid black", padding: 10, marginBottom: 20 }}
      >
        <h2>O Grupie</h2>
        {groupInfo ? (
          <div>
            <p>
              <strong>Opis:</strong> {groupInfo.description}
            </p>
            <p>
              <strong>Kontakt:</strong> {groupInfo.contact}
            </p>
          </div>
        ) : (
          <p>Brak informacji.</p>
        )}
      </section>

      {/* SEKCJA WYDARZENIA */}
      <section
        style={{ border: "1px solid black", padding: 10, marginBottom: 20 }}
      >
        <h2>Wydarzenia</h2>
        {events.map((evt) => (
          <div key={evt.id} style={{ marginBottom: 15 }}>
            <h3>
              {evt.name} ({new Date(evt.date).toLocaleDateString()})
            </h3>
            <p>{evt.description}</p>
            {/* Wyświetlanie zdjęć eventu */}
            {evt.images &&
              evt.images.map((img) => (
                <img
                  key={img.id}
                  src={getImageUrl(img.file_path)}
                  alt="evt"
                  width="100"
                  style={{ marginRight: 5 }}
                />
              ))}
          </div>
        ))}
      </section>

      {/* SEKCJA PROJEKTY */}
      <section style={{ border: "1px solid black", padding: 10 }}>
        <h2>Projekty</h2>
        {projects.map((proj) => (
          <div
            key={proj.id}
            style={{
              borderBottom: "1px solid gray",
              paddingBottom: 10,
              marginBottom: 10,
            }}
          >
            <h3>{proj.name}</h3>
            <p>Technologie: {proj.technologies}</p>
            <p>{proj.description}</p>

            {/* Galeria projektu */}
            <div>
              <h4>Zdjęcia:</h4>
              {proj.images &&
                proj.images.map((img) => (
                  <img
                    key={img.id}
                    src={getImageUrl(img.file_path)}
                    alt="proj"
                    width="100"
                    style={{ marginRight: 5 }}
                  />
                ))}
            </div>

            {/* Pliki Wykonywalne (Download) */}
            <div>
              <h4>Pobierz:</h4>
              {proj.executable && proj.executable.length > 0 ? (
                proj.executable.map((exe) => (
                  <div key={exe.id}>
                    <a
                      href={`${API_URL}/api/download/executable/${exe.id}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <button>
                        Pobierz {exe.platform} (v{exe.version})
                      </button>
                    </a>
                  </div>
                ))
              ) : (
                <p>Brak plików do pobrania.</p>
              )}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
