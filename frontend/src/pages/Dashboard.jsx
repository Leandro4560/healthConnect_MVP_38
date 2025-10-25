import { userAuth } from "../context/Authcontext";
import DashboardPatient from "./dashboard/DashboardPatient";
import DashboardDoctor from "./dashboard/DashboardDoctor";
import DashboardAdmin from "./dashboard/DashboardAdmin";

const Dashboard = () => {
  const { user } = userAuth();

  if (!user) return null;

  // user.role puede venir en diferentes formatos; normalizamos a minúsculas
  const role = (user.role || user.role?.value || "").toString().toLowerCase();

  if (role.includes("doctor")) return <DashboardDoctor />;
  if (role.includes("admin")) return <DashboardAdmin />;
  // por defecto paciente
  return <DashboardPatient />;
};

export default Dashboard;
