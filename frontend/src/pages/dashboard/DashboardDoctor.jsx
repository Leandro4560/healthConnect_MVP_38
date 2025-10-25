import { useEffect, useState } from "react";
import { userAuth } from "../../context/Authcontext";

const API_URL = import.meta.env.VITE_APP_API_URL || "http://localhost:8000/api/v1";

const DashboardDoctor = () => {
  const { user } = userAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const token = localStorage.getItem("hc_token");

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    fetch(`${API_URL}/appointments/doctor`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => setAppointments(data || []))
      .catch((e) => setError(e.message || "Error"))
      .finally(() => setLoading(false));
  }, [token]);

  const handleCancel = async (id) => {
    if (!confirm("¿Cancelar esta cita?")) return;
    try {
      const res = await fetch(`${API_URL}/appointments/${id}/cancel`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Error al cancelar");
      const updated = await res.json();
      setAppointments((s) => s.map((a) => (a.id === updated.id ? updated : a)));
    } catch (e) {
      alert(e.message || "Error");
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl mb-4">Panel Doctor</h2>
      <p>Hola {user.full_name || user.name || user.email}</p>

      <section className="mt-6">
        <h3 className="text-xl">Citas asignadas</h3>
        {loading && <p>Cargando...</p>}
        {error && <p className="text-red-500">{error}</p>}
        <ul>
          {appointments.length === 0 && !loading ? (
            <li>No tienes citas próximas.</li>
          ) : (
            appointments.map((a) => (
              <li key={a.id} className="py-2 border-b flex justify-between">
                  <div>
                  <div>Paciente: {a.patient?.full_name || a.patient?.name || a.patient?.email}</div>
                  <div>Inicio: {a.start_time}</div>
                  <div>Estado: {a.status}</div>
                  {a.video_url && (
                    <div>
                      Enlace Meet: <a href={a.video_url} target="_blank" rel="noopener noreferrer" className="text-blue-600">Entrar a la reunión</a>
                    </div>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  <button onClick={() => handleCancel(a.id)} className="px-2 py-1 bg-red-600 text-white rounded">
                    Cancelar
                  </button>
                </div>
              </li>
            ))
          )}
        </ul>
      </section>
    </div>
  );
};

export default DashboardDoctor;
