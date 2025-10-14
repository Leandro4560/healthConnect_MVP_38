import Logo from "../assets/logo/Logo.svg";
import RegisterForm from "../components/user-register/RegisterForm";

const Register = () => {
  return (
    <div className="h-dvh flex flex-col justify-evenly items-center bg-gradient-to-r from-primary-700 to-secondary">
      <div className="w-80 h-[650px] bg-primary-100 rounded-2xl">
        <div className="h-56 flex flex-col justify-around items-center">
          <figure className="w-28 h-28 ">
            <img
              src={Logo}
              alt="logo-empresa"
              className="w-full h-full rounded-b-4xl object-contain"
            />
          </figure>
          <h1 className="text-2xl">Te damos la bienvenida</h1>
          <h3 className="text-2xl">¡Registrate!</h3>
        </div>
        <RegisterForm />
      </div>
    </div>
  );
};
export default Register;
