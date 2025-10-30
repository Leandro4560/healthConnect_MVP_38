import { userAuth } from "../context/Authcontext";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const { user, signOut } = userAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      // si no hay usuario lo enviamos a login
      navigate("/login", { replace: true });
    }
  }, [user, navigate]);

  if (!user) return null;

  return (
    <div>
      <h1 className="text-2xl">Bienvenido: {user.full_name || user.name || user.email}</h1>
      <div style={{ marginTop: 12 }}>
        <button onClick={() => navigate('/dashboard')}>Ir al dashboard</button>
        <button style={{ marginLeft: 8 }} onClick={signOut}>Cerrar sesión</button>
      </div>
    </div>
  );
};

export default Home;
