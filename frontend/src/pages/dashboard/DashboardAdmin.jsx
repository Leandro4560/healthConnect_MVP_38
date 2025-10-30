import { useEffect, useState } from "react";
import { userAuth } from "../../context/Authcontext";
import { API_URL, api } from "../../lib/api";
import { FiSettings, FiUsers } from "react-icons/fi";

const DashboardAdmin = () => {
  const { user } = userAuth();
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("hc_token");

  useEffect(() => {
    // Como no hay endpoint de admin para todas las citas, mostramos un mensaje y consejos
    setLoading(false);
  }, []);

  return (
    <div className="p-6">
      <header className="flex items-center justify-between bg-gradient-to-r from-violet-600 to-pink-600 text-white p-4 rounded-lg shadow-md">
        <div>
          <h2 className="text-2xl font-semibold">Panel Admin</h2>
          <p className="text-sm opacity-90">Hola {user.full_name || user.name || user.email}</p>
        </div>
        <div className="flex gap-3">
          <div className="flex items-center gap-2 bg-white/10 px-3 py-2 rounded">
            <FiUsers /> <span className="text-sm">Usuarios</span>
          </div>
          <div className="flex items-center gap-2 bg-white/10 px-3 py-2 rounded">
            <FiSettings /> <span className="text-sm">Config</span>
          </div>
        </div>
      </header>

      <section className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 bg-white rounded shadow-sm">
          <h3 className="text-lg font-medium">Acciones administrativas</h3>
          <p className="mt-2 text-slate-700">Actualmente la API expone operaciones por usuario (citas, registros). Si necesita funcionalidades extra (listar todos los usuarios, eliminar, roles), hay que añadir endpoints en el backend.</p>
          <p className="mt-2 text-slate-700">Puedes usar <code className="bg-slate-100 px-1 rounded">/register</code> para crear usuarios, y revisar la base de datos desde el backend.</p>
        </div>

        <div className="p-4 bg-white rounded shadow-sm">
          <h3 className="text-lg font-medium">Sugerencias</h3>
          <ul className="list-disc list-inside mt-2 text-slate-700">
            <li>Agregar endpoints para administración (listar usuarios, asignar roles, auditar cambios).</li>
            <li>Crear paneles con métricas (nuevos usuarios, citas por día, uso de meeting).</li>
            <li>Considerar permisos más finos y auditoría de acciones sensibles.</li>
          </ul>
        </div>
      </section>
    </div>
  );
};

export default DashboardAdmin;
