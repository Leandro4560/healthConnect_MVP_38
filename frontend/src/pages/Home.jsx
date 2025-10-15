import { userAuth } from "../context/Authcontext";

const Home = () => {
  const { user, signOut } = userAuth();
  return (
    <div>
      <h1 className="text-2xl">Bienvenido: {user.full_name}</h1>
      <button onClick={signOut}>Cerrar sesión</button>
    </div>
  );
};

export default Home;
