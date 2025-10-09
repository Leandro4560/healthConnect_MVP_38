import { useState } from "react";
import { FaRegUser } from "react-icons/fa";
import { MdOutlineEmail } from "react-icons/md";
import { MdOutlineVisibilityOff } from "react-icons/md";
import { MdOutlineVisibility } from "react-icons/md";
import Logo from "../assets/logo/Logo.svg";

const Register = () => {
  const initialForm = {
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  };

  const [formRegister, setFormRegister] = useState(initialForm);
  const [visibilityInput, setVisibilityInput] = useState(false);
  const [visibilityInputConfirm, setVisibilityInputConfirm] = useState(false);

  const handleChangeVisibility = () => {
    setVisibilityInput(!visibilityInput);
  };
  const handleChangeVisibilityConfirm = () => {
    setVisibilityInputConfirm(!visibilityInputConfirm);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormRegister({
      ...formRegister,
      [name]: value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(formRegister);
  };

  return (
    <div className="h-dvh flex flex-col justify-evenly items-center bg-gradient-to-r from-primary-700 to-secondary">
      <div className="w-80 h-[650px] bg-primary-100 rounded-2xl">
        <div className="h-56 flex flex-col justify-around items-center">
          <div className="w-28 h-28">
            <img
              src={Logo}
              alt="logo-empresa"
              className="w-full h-full object-contain"
            />
          </div>

          <h1 className="text-2xl">Te damos la bienvenida</h1>
          <h3 className="text-2xl">¡Registrate!</h3>
        </div>

        <form
          className="h-[368px] flex flex-col justify-around items-center"
          onSubmit={handleSubmit}>
          <label htmlFor="" className="w-64 relative">
            <input
              type="text"
              name="name"
              placeholder="Nombre"
              value={formRegister.name}
              onChange={handleChange}
              className="w-full h-10 bg-white rounded-lg pl-2 focus:outline focus:outline-sky-500"
            />
            <FaRegUser className="size-5 absolute bottom-1/4 right-3" />
          </label>
          <label htmlFor="" className="w-[250px] relative">
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formRegister.email}
              onChange={handleChange}
              className="w-full h-10 bg-white rounded-lg pl-2 focus:outline focus:outline-sky-500"
            />
            <MdOutlineEmail className="size-5 absolute bottom-1/4 right-3" />
          </label>
          <label htmlFor="" className="w-[250px] relative">
            <input
              type={!visibilityInput ? "password" : "text"}
              name="password"
              placeholder="Contraseña"
              value={formRegister.password}
              onChange={handleChange}
              autoComplete="false"
              className="w-full h-10 bg-white rounded-lg pl-2 focus:outline focus:outline-sky-500"
            />
            <div onClick={handleChangeVisibility}>
              {!visibilityInput ? (
                <MdOutlineVisibilityOff className="size-5 absolute bottom-1/4 right-3" />
              ) : (
                <MdOutlineVisibility className="size-5 absolute bottom-1/4 right-3" />
              )}
            </div>
          </label>
          <label htmlFor="" className="w-[250px] relative">
            <input
              type={!visibilityInputConfirm ? "password" : "text"}
              name="confirmPassword"
              placeholder="Confirma contraseña"
              value={formRegister.confirmPassword}
              onChange={handleChange}
              autoComplete="false"
              className="w-full h-10 bg-white rounded-lg pl-2 focus:outline focus:outline-sky-500"
            />
            <div onClick={handleChangeVisibilityConfirm}>
              {!visibilityInputConfirm ? (
                <MdOutlineVisibilityOff className="size-5 absolute bottom-1/4 right-3" />
              ) : (
                <MdOutlineVisibility className="size-5 absolute bottom-1/4 right-3" />
              )}
            </div>
          </label>

          <button type="submit" className="w-64 h-10 bg-[#20ABF0] rounded-lg">
            Registrate
          </button>
        </form>
      </div>
    </div>
  );
};
export default Register;
