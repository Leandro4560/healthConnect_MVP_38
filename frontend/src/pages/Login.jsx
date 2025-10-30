import Logo from "../assets/logo/Logo.svg";
import LoginForm from "../components/user-login/LoginForm";
import RegisterForm from "../components/user-register/RegisterForm";
import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { userAuth } from "../context/Authcontext";

export const Login = () => {
  const [showRegister, setShowRegister] = useState(false);
  const [searchParams] = useSearchParams();
  const { setTokenFromString } = userAuth();

  useEffect(() => {
    // Si la URL contiene token (OAuth), procesarlo
    const token = searchParams.get("token");
    const refresh = searchParams.get("refresh");
    if (token) {
      (async () => {
        await setTokenFromString({ access_token: token, refresh_token: refresh });
      })();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="h-dvh flex flex-col justify-evenly items-center bg-gradient-to-r from-primary-700 to-secondary">
      <div className="w-80 h-[650px] md:w-[650px] md:h-[730px]  bg-primary-100 rounded-2xl">
        <div className="h-56 flex flex-col justify-around items-center">
          <figure className="w-28 h-28 ">
            <img
              src={Logo}
              alt="logo-empresa"
              className="w-full h-full rounded-b-4xl object-cover"
            />
          </figure>

          <h3 className="text-2xl md:text-3xl">Inicio de sesión</h3>
        </div>
        {/* Mostrar Login o Register en la misma ruta según el estado */}
        {!showRegister ? (
          <>
            <LoginForm onShowRegister={() => setShowRegister(true)} />
          </>
        ) : (
          <RegisterForm />
        )}
        <div style={{ textAlign: "center", marginTop: 8 }}>
          {!showRegister ? (
            <button onClick={() => setShowRegister(true)} className="text-sm text-primary-500">
              ¿No tienes cuenta? Regístrate
            </button>
          ) : (
            <button onClick={() => setShowRegister(false)} className="text-sm text-primary-500">
              Volver al login
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Login;
