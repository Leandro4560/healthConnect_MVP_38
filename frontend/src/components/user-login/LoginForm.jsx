import { useEffect, useState } from "react";
import { MdOutlineEmail } from "react-icons/md";
import { MdOutlineVisibilityOff } from "react-icons/md";
import { MdOutlineVisibility } from "react-icons/md";
import { useValidationsFormRegister } from "../../hooks/useValidationsFormRegister";
import { userAuth } from "../../context/Authcontext";
import ImgGoggle from "../../assets/google.svg";
import { Link } from "react-router-dom";

const LoginForm = () => {
  const { signInWithGoogle, login } = userAuth();
  const initialForm = {
    email: "",
    password: "",
  };

  const [formLogin, setFormLogin] = useState(initialForm);
  const [visibilityInput, setVisibilityInput] = useState(false);

  const { errors, handleOnBlur } = useValidationsFormRegister();
  const [emptyValidInputs, setEmptyValidInputs] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loginError, setLoginError] = useState(null);

  const handleChangeVisibility = () => {
    setVisibilityInput(!visibilityInput);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormLogin({
      ...formLogin,
      [name]: value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const hasNoErrors = !Object.values(errors).some((v) => v === true);

    if (!formLogin.email || !formLogin.password) {
      setEmptyValidInputs(true);
      return;
    }

    setEmptyValidInputs(false);

    if (hasNoErrors) {
      // Intentar login usando el contexto
      (async () => {
        try {
          setSubmitting(true);
          setLoginError(null);
          await login(formLogin.email, formLogin.password);
        } catch (err) {
          setLoginError(err.message || "Error al iniciar sesión");
        } finally {
          setSubmitting(false);
        }
      })();
    }
  };

  useEffect(() => {
    let time;

    time = setTimeout(() => {
      setEmptyValidInputs(false);
    }, 3000);

    return () => {
      clearTimeout(time);
    };
  }, [emptyValidInputs]);

  const styleInput =
    "w-64 h-10 bg-white rounded-lg pl-2 focus:outline focus:outline-sky-500 text-lg";
  const styleInputError =
    "w-64 rounded-lg text-center p-0.5 font-medium text-red-500 bg-red-100/80 tracking-wide";

  return (
    <div className=" flex flex-col justify-evenly items-center ">
      <form
        className="w-72 h-60 md:w-[380px] md:h-[250px] flex flex-col justify-evenly items-center rounded-2xl mb-3 bg-primary-600"
        onSubmit={handleSubmit}>
        <label className="w-[250px] relative">
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formLogin.email}
            onChange={handleChange}
            onBlur={handleOnBlur}
            className={styleInput}
          />
          <MdOutlineEmail className="size-5 absolute bottom-1/4 right-3" />
        </label>

        {errors.validEmail ? (
          <p className={styleInputError}>{errors.messageValidEmail}</p>
        ) : (
          ""
        )}

        <label className="w-[250px] relative">
          <input
            type={!visibilityInput ? "password" : "text"}
            name="password"
            placeholder="Contraseña"
            value={formLogin.password}
            autoComplete="false"
            onChange={handleChange}
            onBlur={handleOnBlur}
            className={styleInput}
          />
          <div onClick={handleChangeVisibility}>
            {!visibilityInput ? (
              <MdOutlineVisibilityOff className="size-5 absolute bottom-1/4 right-3" />
            ) : (
              <MdOutlineVisibility className="size-5 absolute bottom-1/4 right-3" />
            )}
          </div>
        </label>
        {errors.validPassword ? (
          <p className={styleInputError}>{errors.messageValidPassword}</p>
        ) : (
          ""
        )}
        {emptyValidInputs ? (
          <p className={styleInputError}>Todos los campos son requeridos</p>
        ) : (
          ""
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-64 h-10 text-lg tracking-wide bg-primary-300 text-white rounded-lg duration-500 ease-out hover:bg-primary-200 hover:text-primary-700 disabled:opacity-50">
          {submitting ? "Cargando..." : "Inicia sesión"}
        </button>
        {loginError ? <p className={styleInputError}>{loginError}</p> : null}
      </form>

      <hr className="w-2xs my-3 md:w-[480px]  " />

        <div className="h-32 flex flex-col justify-evenly items-center ">
        <button
          className="w-64 h-10 flex justify-evenly items-center  bg-white tracking-wide rounded-lg"
          onClick={signInWithGoogle}>
          <img src={ImgGoggle} alt="logo-google" className="w-6" />
          Continua con Google
        </button>
        <p className="">¿No tienes cuenta?</p>

        <button
          onClick={() => onShowRegister && onShowRegister()}
          className="font-bold text-primary-400 bg-transparent border-none">
          Registrate aqui
        </button>
      </div>
    </div>
  );
};
export default LoginForm;
