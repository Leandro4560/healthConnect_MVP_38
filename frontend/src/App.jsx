import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import Home from "./pages/Home";
import Login from "./pages/Login";
import AuthSuccess from "./pages/AuthSuccess";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import Dashboard from "./pages/Dashboard";
import { AuthContextProvider } from "./context/Authcontext";

function App() {
  return (
    <>
      <BrowserRouter>
        <AuthContextProvider>
          <Routes>
            {/* Minimal routes: landing/login (/) and protected /dashboard */}
            <Route exact path="/" element={<Login />} />
            <Route exact path="/auth/success" element={<AuthSuccess />} />
            <Route
              exact
              path="/dashboard"
              element={
                <RoleRoute allowedRoles={["Patient", "Doctor", "Admin"]}>
                  <Dashboard />
                </RoleRoute>
              }
            />
            <Route element={<h1 className="text-9xl"> Not Found!</h1>} />
          </Routes>
        </AuthContextProvider>
      </BrowserRouter>
    </>
  );
}

export default App;
