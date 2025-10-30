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
    apiFetch("appointments/patient", { method: "GET", headers: { Authorization: `Bearer ${token}` } })
      .then((data) => setAppointments(data || []))
      .catch((e) => setError(e.response?.detail || e.message || "Error"))
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
  const [formErrors, setFormErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError(null);
      // validar campos básicos en cliente para evitar 422
      const errs = {};
      if (!doctorId) errs.doctorId = "Seleccione un doctor válido";
      if (!startTime) errs.startTime = "Fecha/hora de inicio requerida";
      if (!endTime) errs.endTime = "Fecha/hora de fin requerida";
      let startIso = null;
      let endIso = null;
      if (startTime) {
        const s = new Date(startTime);
        if (isNaN(s.getTime())) errs.startTime = "Formato de fecha inválido";
        else startIso = s.toISOString();
      }
      if (endTime) {
        const eDate = new Date(endTime);
        if (isNaN(eDate.getTime())) errs.endTime = "Formato de fecha inválido";
        else endIso = eDate.toISOString();
      }
      if (startIso && endIso && new Date(startIso) >= new Date(endIso)) {
        errs.range = "La fecha de fin debe ser posterior al inicio";
      }
      setFormErrors(errs);
      if (Object.keys(errs).length > 0) return;

      setLoading(true);
      const payload = {
        doctor_id: Number(doctorId),
        start_time: startIso,
        end_time: endIso,
        is_virtual: Boolean(isVirtual),
        description,
      };
      const created = await apiFetch("appointments/", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });
      onCreated(created);
      // limpiar form
      setDescription("");
      setStartTime("");
      setEndTime("");
    } catch (err) {
      console.error("error creating appointment", err);
      setError(err.response?.detail || err.message || "Error creando cita");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 max-w-md bg-white p-4 rounded shadow-sm">
      <label className="flex flex-col">
        <span className="text-sm font-medium">Doctor ID</span>
        <input value={doctorId} onChange={(e) => setDoctorId(e.target.value)} className="mt-1 p-2 border rounded" />
        {formErrors.doctorId && <small className="text-red-500">{formErrors.doctorId}</small>}
      </label>

      <label className="flex flex-col">
        <span className="text-sm font-medium">Fecha / Hora inicio</span>
        <input type="datetime-local" value={startTime} onChange={(e) => setStartTime(e.target.value)} className="mt-1 p-2 border rounded" />
        {formErrors.startTime && <small className="text-red-500">{formErrors.startTime}</small>}
      </label>

      <label className="flex flex-col">
        <span className="text-sm font-medium">Fecha / Hora fin</span>
        <input type="datetime-local" value={endTime} onChange={(e) => setEndTime(e.target.value)} className="mt-1 p-2 border rounded" />
        {formErrors.endTime && <small className="text-red-500">{formErrors.endTime}</small>}
      </label>

      {formErrors.range && <p className="text-red-500">{formErrors.range}</p>}

      <label className="flex items-center gap-2">
        <input type="checkbox" checked={isVirtual} onChange={(e) => setIsVirtual(e.target.checked)} />
        <span>¿Cita virtual (Google Meet)?</span>
      </label>

      <label className="flex flex-col">
        <span className="text-sm font-medium">Descripción (opcional)</span>
        <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="mt-1 p-2 border rounded w-full" />
      </label>

      {error && <p className="text-red-500">{error}</p>}
      <button disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
        {loading ? "Creando..." : "Agendar cita"}
      </button>
    </form>
  );
};

export default DashboardPatient;
