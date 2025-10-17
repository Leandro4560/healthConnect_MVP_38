import { Link } from "react-router-dom";
import Logo from "../assets/logo/Logo.svg";
import RegisterForm from "../components/user-register/RegisterForm";

const Register = () => {
  return (
    <div className="h-dvh flex flex-col justify-evenly items-center bg-gradient-to-r from-primary-700 to-secondary">
      <div className="w-80 h-[650px] md:w-[650px] md:h-[730px] md:flex flex-col justify-evenly  bg-primary-100 rounded-2xl">
        <div className="h-56 flex flex-col justify-around items-center">
          <figure className="w-28 h-28 ">
            <img
              src={Logo}
              alt="logo-empresa"
              className="w-full h-full rounded-b-4xl object-contain"
            />
          </figure>
          <h1 className="text-2xl md:text-3xl">Registrate</h1>
          <div className="flex">
            <p className="pr-3">¿Ya tienes cuenta?</p>
            <Link to="/login" className="font-bold  text-primary-400">
              Inicia sesión
            </Link>
          </div>
        </div>
        <RegisterForm />
      </div>
    </div>
  );
};
export default Register;
