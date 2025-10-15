import Logo from "../assets/logo/Logo.svg";
import LoginForm from "../components/user-login/LoginForm";

export const Login = () => {
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
        <LoginForm />
      </div>
    </div>
  );
};

export default Login;
