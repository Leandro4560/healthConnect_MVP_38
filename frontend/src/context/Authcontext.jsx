import { createContext } from "react";
import { useContext } from "react";
import { useState } from "react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../supabase/supabase.config";

const AuthContext = createContext();

export const AuthContextProvider = ({ children }) => {
  const navigate = useNavigate();
  const [user, setUser] = useState([]);

  async function signInWithGoogle() {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "google",
      });

      if (error) throw new Error("Error durante la autenticación");
      console.log(data);

      return data;
    } catch (error) {
      console.log(error);
    }
  }

  async function signOut() {
    const { error } = await supabase.auth.signOut();
    if (error) throw new Error("Error durante el cierre de sesión");
    console.log(error);
  }

  useEffect(() => {
    const { data: authListener } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log("supabase session: ", event);
        if (session == null) {
          navigate("/login", { replace: true });
        } else {
          setUser(session?.user?.user_metadata);
          //  console.log("data del usuario", session?.user);
          navigate("/", { replace: true });
        }
      }
    );
    return () => {
      authListener.subscription;
    };
  }, []);

  return (
    <AuthContext.Provider value={{ signInWithGoogle, signOut, user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const userAuth = () => useContext(AuthContext);
