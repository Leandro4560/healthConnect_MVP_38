import { useEffect, useState } from "react";
import { userAuth } from "../../context/Authcontext";
import { API_URL, apiFetch } from "../../lib/api";

const DashboardPatient = () => {
  const { user } = userAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const token = localStorage.getItem("hc_token");

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    apiFetch("/appointments/patient", { method: "GET", headers: { Authorization: `Bearer ${token}` } })
      .then((res) => setAppointments(res.data || []))
      .catch((e) => setError(e.response?.data?.detail || e.message || "Error"))
      .finally(() => setLoading(false));
  }, [token]);

  return (
    <div className="p-4">
      <h2 className="text-2xl mb-4">Panel Paciente</h2>
      <p>Hola {user.full_name || user.name || user.email}</p>

      <section className="mt-6">
        <h3 className="text-xl">Tus citas próximas</h3>
        {loading && <p>Cargando...</p>}
        {error && <p className="text-red-500">{error}</p>}
        <ul>
          {appointments.length === 0 && !loading ? (
            <li>No tienes citas próximas.</li>
          ) : (
            appointments.map((a) => (
              <li key={a.id} className="py-2 border-b">
                <div>Doctor: {a.doctor?.full_name || a.doctor?.name || a.doctor?.email}</div>
                <div>Inicio: {a.start_time}</div>
                <div>Estado: {a.status}</div>
                {a.video_url && (
                  <div>
                    Enlace Meet: <a href={a.video_url} target="_blank" rel="noopener noreferrer" className="text-blue-600">Entrar a la reunión</a>
                  </div>
                )}
              </li>
            ))
          )}
        </ul>
      </section>

      <section className="mt-6">
        <h3 className="text-xl">Agendar nueva cita</h3>
        <AppointmentForm token={token} onCreated={(c) => setAppointments((s) => [c, ...s])} />
      </section>
    </div>
  );
};

const AppointmentForm = ({ token, onCreated }) => {
  const [doctorId, setDoctorId] = useState(1);
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [isVirtual, setIsVirtual] = useState(true);
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch("/appointments/", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify({ doctor_id: Number(doctorId), start_time: startTime, end_time: endTime, is_virtual: Boolean(isVirtual), description }),
      });
      const data = res.data;
      onCreated && onCreated(data);
      setDoctorId(1);
      setStartTime("");
      setEndTime("");
      setDescription("");
      setIsVirtual(true);
    } catch (e) {
      setError(e.message || "Error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 max-w-md">
      <label>
        Doctor ID:
        <input value={doctorId} onChange={(e) => setDoctorId(e.target.value)} className="ml-2" />
      </label>
      <label>
        Fecha/Hora (ISO):
        <input value={startTime} onChange={(e) => setStartTime(e.target.value)} className="ml-2" />
      </label>
      <label>
        Fin (ISO):
        <input value={endTime} onChange={(e) => setEndTime(e.target.value)} className="ml-2" />
      </label>
      <label className="flex items-center gap-2">
        <input type="checkbox" checked={isVirtual} onChange={(e) => setIsVirtual(e.target.checked)} />
        <span>¿Cita virtual (Google Meet)?</span>
      </label>
      <label>
        Descripción:
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="ml-2 w-full" />
      </label>
      {error && <p className="text-red-500">{error}</p>}
      <button disabled={loading} className="px-3 py-1 bg-blue-600 text-white rounded">
        {loading ? "Creando..." : "Agendar cita"}
      </button>
    </form>
  );
};

export default DashboardPatient;
