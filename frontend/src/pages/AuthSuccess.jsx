import { useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { userAuth } from "../context/Authcontext";

const AuthSuccess = () => {
  const [searchParams] = useSearchParams();
  const { setTokenFromString } = userAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get("token");
    const refresh = searchParams.get("refresh");
    if (token) {
      // Guardar token y refresh y cargar usuario
      (async () => {
        await setTokenFromString({ access_token: token, refresh_token: refresh });
      })();
    } else {
      // si no hay token, ir a login
      navigate("/login", { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <div className="p-4">Procesando login... redirigiendo...</div>;
};

export default AuthSuccess;
