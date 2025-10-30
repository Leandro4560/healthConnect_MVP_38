import { useEffect, useState } from "react";
import { userAuth } from "../../context/Authcontext";
import { API_URL, api } from "../../lib/api";
import { FiVideo, FiUser, FiCalendar } from "react-icons/fi";

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
    <div className="p-6">
      <header className="flex items-center justify-between bg-gradient-to-r from-sky-500 to-indigo-600 text-white p-4 rounded-lg shadow-md">
        <div>
          <h2 className="text-2xl font-semibold">Panel Doctor</h2>
          <p className="text-sm opacity-90">Hola {user.full_name || user.name || user.email}</p>
        </div>
        <div className="flex gap-3">
          <div className="flex items-center gap-2 bg-white/10 px-3 py-2 rounded">
            <FiUser /> <span className="text-sm">{appointments.length} citas</span>
          </div>
          <div className="flex items-center gap-2 bg-white/10 px-3 py-2 rounded">
            <FiCalendar /> <span className="text-sm">Próximas: {appointments.filter(a=>a.status!=='cancelled').length}</span>
          </div>
        </div>
      </header>

      <section className="mt-6">
        <h3 className="text-lg font-medium mb-3">Citas asignadas</h3>
        {loading && <p>Cargando...</p>}
        {error && <p className="text-red-500">{error}</p>}

        <ul className="flex flex-col gap-3">
          {appointments.length === 0 && !loading ? (
            <li className="p-4 bg-white rounded shadow-sm">No tienes citas próximas.</li>
          ) : (
            appointments.map((a) => (
              <li key={a.id} className="p-4 bg-white rounded shadow-sm flex justify-between items-start">
                <div className="flex gap-4">
                  <div className="flex flex-col">
                    <div className="text-sm text-slate-600">Paciente</div>
                    <div className="font-medium">{a.patient?.full_name || a.patient?.name || a.patient?.email}</div>
                  </div>
                  <div className="flex flex-col">
                    <div className="text-sm text-slate-600">Inicio</div>
                    <div className="font-medium">{a.start_time ? new Date(a.start_time).toLocaleString() : '-'}</div>
                  </div>
                  <div className="flex flex-col">
                    <div className="text-sm text-slate-600">Tipo</div>
                    <div className="flex items-center gap-2">
                      {a.is_virtual ? <FiVideo className="text-sky-500" /> : <FiCalendar />}
                      <span className="text-sm">{a.is_virtual ? 'Virtual' : 'Presencial'}</span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-3">
                  <StatusBadge status={a.status} />
                  <div className="flex gap-2">
                    {a.video_url && (
                      <a href={a.video_url} target="_blank" rel="noopener noreferrer" className="px-3 py-1 bg-sky-600 text-white rounded text-sm">Entrar</a>
                    )}
                    <button onClick={() => handleCancel(a.id)} className="px-3 py-1 bg-red-600 text-white rounded text-sm">Cancelar</button>
                  </div>
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

const StatusBadge = ({ status }) => {
  const s = (status || '').toLowerCase();
  if (s === 'confirmed' || s === 'accepted' || s === 'active')
    return <span className="px-3 py-1 rounded-full bg-green-100 text-green-700 text-sm">{status}</span>;
  if (s === 'pending' || s === 'waiting')
    return <span className="px-3 py-1 rounded-full bg-yellow-100 text-yellow-700 text-sm">{status}</span>;
  if (s === 'cancelled' || s === 'canceled')
    return <span className="px-3 py-1 rounded-full bg-red-100 text-red-700 text-sm">{status}</span>;
  return <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-sm">{status || 'desconocido'}</span>;
};
