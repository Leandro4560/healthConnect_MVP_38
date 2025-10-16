import { useEffect, useState } from "react";
import { FaRegUser } from "react-icons/fa";
import { MdOutlineEmail } from "react-icons/md";
import { MdOutlineVisibilityOff } from "react-icons/md";
import { MdOutlineVisibility } from "react-icons/md";
import { useValidationsFormRegister } from "../../hooks/useValidationsFormRegister";

const RegisterForm = () => {
  const initialForm = {
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  };

  const [formRegister, setFormRegister] = useState(initialForm);
  const [visibilityInput, setVisibilityInput] = useState(false);
  const [visibilityInputConfirm, setVisibilityInputConfirm] = useState(false);

  const { errors, handleOnBlur } = useValidationsFormRegister();
  const [emptyValidInputs, setEmptyValidInputs] = useState(false);

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

    const hasNoErrors = !Object.values(errors).some((v) => v === true);

    if (
      !formRegister.name ||
      !formRegister.email ||
      !formRegister.password ||
      !formRegister.confirmPassword
    ) {
      setEmptyValidInputs(true);

      return;
    }

    setEmptyValidInputs(false);

    if (hasNoErrors) {
      console.log(formRegister);
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
        className="w-72 h-[368px]  flex flex-col justify-around items-center  rounded-2xl bg-primary-600"
        onSubmit={handleSubmit}>
        <label className="w-64 relative">
          <input
            type="text"
            name="name"
            placeholder="Nombre"
            value={formRegister.name}
            onChange={handleChange}
            onBlur={handleOnBlur}
            className={styleInput}
          />
          <FaRegUser className="size-5 absolute bottom-1/4 right-3" />
        </label>
        {errors.minName ? (
          <p className={styleInputError}>{errors.messageMinName}</p>
        ) : (
          ""
        )}
        {errors.validName ? (
          <p className={styleInputError}>{errors.messageValidName}</p>
        ) : (
          ""
        )}

        <label className="w-[250px] relative">
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formRegister.email}
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
            value={formRegister.password}
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
        <label className="w-[250px] relative">
          <input
            type={!visibilityInputConfirm ? "password" : "text"}
            name="confirmPassword"
            placeholder="Confirma contraseña"
            value={formRegister.confirmPassword}
            autoComplete="false"
            onChange={handleChange}
            onBlur={handleOnBlur}
            className={styleInput}
          />
          <div onClick={handleChangeVisibilityConfirm}>
            {!visibilityInputConfirm ? (
              <MdOutlineVisibilityOff className="size-5 absolute bottom-1/4 right-3" />
            ) : (
              <MdOutlineVisibility className="size-5 absolute bottom-1/4 right-3" />
            )}
          </div>
        </label>
        {errors.validConfirmPassword ? (
          <p className={styleInputError}>{errors.messageConfirmPassword}</p>
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
          className="w-64 h-10 text-lg tracking-wide bg-primary-300 text-white rounded-lg duration-500 ease-out hover:bg-primary-200 hover:text-primary-700">
          Registrate
        </button>
      </form>
    </div>
  );
};
export default RegisterForm;
