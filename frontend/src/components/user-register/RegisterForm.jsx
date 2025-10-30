import { useEffect, useState } from "react";
import { FaRegUser } from "react-icons/fa";
import { MdOutlineEmail } from "react-icons/md";
import { MdOutlineVisibilityOff } from "react-icons/md";
import { MdOutlineVisibility } from "react-icons/md";
import useValidationsFormRegister, { isInstitutionalEmail } from "../../hooks/useValidationsFormRegister";
import { userAuth } from "../../context/Authcontext";
import { useNavigate } from "react-router-dom";

const RegisterForm = () => {
  const initialForm = {
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "patient",
  };

  const [formRegister, setFormRegister] = useState(initialForm);
  const [visibilityInput, setVisibilityInput] = useState(false);
  const [visibilityInputConfirm, setVisibilityInputConfirm] = useState(false);
  const [licenseNumber, setLicenseNumber] = useState("");
  const [licenseError, setLicenseError] = useState(null);

  const { errors, handleOnBlur } = useValidationsFormRegister();
  const [emptyValidInputs, setEmptyValidInputs] = useState(false);
  const { register } = userAuth();
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);
  const [registerError, setRegisterError] = useState(null);

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

  const handleLicenseChange = (e) => {
    setLicenseNumber(e.target.value);
    if (e.target.value.trim().length === 0) setLicenseError("Número de licencia requerido");
    else setLicenseError(null);
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

    // si el rol es doctor, validar email institucional y licencia
    if (formRegister.role === "doctor") {
      const okEmail = isInstitutionalEmail(formRegister.email);
      if (!okEmail) {
        setRegisterError("Para registrar como doctor use un correo institucional (ej: correo de hospital o clínica). Si no tiene, contacte al administrador.");
        return;
      }
      if (!licenseNumber || licenseNumber.trim().length === 0) {
        setLicenseError("Número de licencia requerido para doctores");
        return;
      }
    }

    if (hasNoErrors) {
      (async () => {
        try {
          setSubmitting(true);
          setRegisterError(null);
          const payload = {
            email: formRegister.email,
            name: formRegister.name,
            password: formRegister.password,
            role: formRegister.role || "patient",
            // campo opcional para backend: numero de licencia si es doctor
            ...(formRegister.role === "doctor" ? { license_number: licenseNumber } : {}),
          };
          await register(payload);
          // Después de registrar, redirigir al landing (login)
          navigate("/", { replace: true });
        } catch (err) {
          setRegisterError(err.message || "Error al registrarse");
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
    <div className="flex flex-col justify-evenly items-center">
      <form
        className="w-80 p-6 flex flex-col justify-around items-center rounded-2xl bg-primary-600 shadow-lg"
        onSubmit={handleSubmit}>
        <h3 className="text-white text-xl font-semibold mb-2">Crea tu cuenta</h3>
        <p className="text-white/80 text-sm mb-4">Selecciona tu tipo de usuario</p>
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
        <div className="w-64 mt-1 mb-2">
          <label className="text-sm text-white/90">Rol</label>
          <select
            name="role"
            value={formRegister.role}
            onChange={(e) =>
              setFormRegister({ ...formRegister, role: e.target.value })
            }
            className="w-64 h-10 bg-white rounded-lg pl-2 text-lg mt-1">
            <option value="patient">Paciente</option>
            <option value="doctor">Doctor</option>
            {/* Admin no expuesto en el formulario público para evitar creación accidental. */}
          </select>
          {formRegister.role === "doctor" && formRegister.email && !formRegister.email.includes("@doctorhospital") ? (
            <p className="text-yellow-200 text-xs mt-1">Sugerencia: si eres doctor usa tu correo @doctorhospital (si corresponde).</p>
          ) : null}
        </div>
        {formRegister.role === "doctor" && (
          <label className="w-64 mt-3 relative">
            <input
              type="text"
              name="license_number"
              placeholder="Número de licencia (ej: COL-123456)"
              value={licenseNumber}
              onChange={handleLicenseChange}
              className={styleInput}
            />
            {licenseError ? <p className="text-yellow-200 text-xs mt-1">{licenseError}</p> : <p className="text-yellow-200 text-xs mt-1">Proporciona tu número de colegiatura para verificación.</p>}
          </label>
        )}
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

        {formRegister.role === "doctor" && formRegister.email && !isInstitutionalEmail(formRegister.email) ? (
          <p className="text-yellow-200 text-xs mt-1">Advertencia: el correo no parece institucional. Se recomienda usar un correo de hospital/clinica o un dominio .org/.edu.</p>
        ) : null}

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
          disabled={submitting}
          className="w-64 h-10 text-lg tracking-wide bg-gradient-to-r from-green-400 to-blue-500 text-white rounded-lg duration-500 ease-out hover:from-green-500 hover:to-blue-600 disabled:opacity-50">
          {submitting ? "Registrando..." : "Regístrate"}
        </button>
        {registerError ? <p className={styleInputError}>{registerError}</p> : null}
      </form>
    </div>
  );
};
export default RegisterForm;
