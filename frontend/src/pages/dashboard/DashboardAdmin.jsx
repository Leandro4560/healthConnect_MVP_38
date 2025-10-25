import { useEffect, useState } from "react";
import { userAuth } from "../../context/Authcontext";

const API_URL = import.meta.env.VITE_APP_API_URL || "http://localhost:8000";

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
    <div className="p-4">
      <h2 className="text-2xl mb-4">Panel Admin</h2>
      <p>Hola {user.full_name || user.name || user.email}</p>
      <section className="mt-6">
        <h3 className="text-xl">Acciones administrativas</h3>
        <p className="mt-2">Actualmente la API expone operaciones por usuario (citas, registros). Si necesita funcionalidades extra (listar todos los usuarios, eliminar, roles), hay que añadir endpoints en el backend.</p>
        <p className="mt-2">Puedes usar /register para crear usuarios, y revisar la base de datos desde el backend.</p>
      </section>
    </div>
  );
};

export default DashboardAdmin;
