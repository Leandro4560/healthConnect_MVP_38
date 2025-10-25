import { Navigate } from "react-router-dom";
import { userAuth } from "../context/Authcontext";

const RoleRoute = ({ children, allowedRoles = [] }) => {
  const { user } = userAuth();
  if (!user) return <Navigate to="/login" replace />;
  const role = (user.role || user.role?.value || "").toString().toLowerCase();
  const ok = allowedRoles.some((r) => role.includes(r.toString().toLowerCase()));
  if (!ok) return <Navigate to="/" replace />;
  return children;
};

export default RoleRoute;
