import { Navigate } from "react-router-dom";
import { userAuth } from "../context/Authcontext";

const ProtectedRoute = ({ children }) => {
  const { user } = userAuth();
  if (!user) return <Navigate to="/login" replace />;
  return children;
};

export default ProtectedRoute;
