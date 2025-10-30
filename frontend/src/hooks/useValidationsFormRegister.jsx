import { useState } from "react";

// Validador utilitario para comprobar si un email pertenece a dominios institucionales
export const isInstitutionalEmail = (email, allowedDomains = []) => {
  if (!email) return false;
  const e = String(email).trim().toLowerCase();
  if (!e.includes("@")) return false;
  // Si se proveen dominios permitidos, chequearlos exactamente
  if (allowedDomains.length > 0) {
    return allowedDomains.some((d) => e.endsWith(`@${d.toLowerCase()}`));
  }

  // Si no se proveen dominios, aplicar heurística: permitir emails institucionales
  // heurística: dominios que contienen 'hospital' o 'clinic' o terminan en .org/.edu/.gov
  const domain = e.split("@")[1] || "";
  if (domain.includes("hospital") || domain.includes("clinic") || domain.endsWith(".org") || domain.endsWith(".edu") || domain.endsWith(".gov")) {
    return true;
  }
  // Por defecto, considerar no institucional
  return false;
};

export const useValidationsFormRegister = () => {
  const [valuePassword, setValuePassword] = useState("");
  const [errors, setErrors] = useState(
    {
      minName: false,
      messageMinName: "",
      validName: false,
      messageValidName: "",
    },
    {
      validEmail: false,
      messageValidEmail: "",
    },
    {
      validPassword: false,
      messageValidPassword: "",
    },
    {
      validConfirmPassword: false,
      messageConfirmPassword: "",
    }
  );

  const handleOnBlur = (e) => {
    const { name, value } = e.target;
    const noSpaces = value.trim();
    const regexName = /^[A-Za-zÀ-ÖØ-öø-ÿÑñ]+(?:\s[A-Za-zÀ-ÖØ-öø-ÿÑñ]+)*$/;
    const regexEmail =
      /^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@([A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}$/i;

    if (name === "name") {
      const messageEmpty = "Campo nombre es requerido";
      const messageValid = "El minimo de caracteres son tres";
      const messageValidNumber = "No se aceptan numeros";

      const isEmptyName = noSpaces.length === 0;
      if (isEmptyName) {
        setErrors((prev) => ({
          ...prev,
          validName: isEmptyName,
          messageValidName: isEmptyName ? messageEmpty : "",
        }));
        return;
      }

      const isValid = noSpaces.length < 3;

      setErrors((prev) => ({
        ...prev,
        minName: isValid,
        messageMinName: isValid ? messageValid : "",
      }));

      const isValidName = !regexName.test(noSpaces);

      setErrors((prev) => ({
        ...prev,
        validName: isValidName,
        messageValidName: isValidName ? messageValidNumber : "",
      }));
    }

    if (name === "email") {
      const messageEmpty = "Campo email es requerido";
      const messageValid = "Email invalido";

      const isEmptyEmail = noSpaces.length === 0;

      if (isEmptyEmail) {
        setErrors((prev) => ({
          ...prev,
          validEmail: isEmptyEmail,
          messageValidEmail: isEmptyEmail ? messageEmpty : "",
        }));

        return;
      }

      const isValidEmail = !regexEmail.test(noSpaces);

      setErrors((prev) => ({
        ...prev,
        validEmail: isValidEmail,
        messageValidEmail: isValidEmail ? messageValid : "",
      }));
    }

    if (name === "password") {
      const messageEmpty = "Campo password es requerido";
      const isEmptyPassword = noSpaces.length === 0;

      setErrors((prev) => ({
        ...prev,
        validPassword: isEmptyPassword,
        messageValidPassword: isEmptyPassword ? messageEmpty : "",
      }));

      setValuePassword(noSpaces);
    }

    if (name === "confirmPassword") {
      const message = "Las contraseñas son distintas";
      const differentPass = valuePassword !== noSpaces;

      setErrors((prev) => ({
        ...prev,
        validConfirmPassword: differentPass,
        messageConfirmPassword: differentPass ? message : "",
      }));
    }
  };
  return { errors, handleOnBlur };
};

export default useValidationsFormRegister;
