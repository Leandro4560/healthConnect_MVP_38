import {BrowserRouter, Routes, Route } from "react-router-dom";
import './App.css'
import Home from "./pages/Home";
import Login from "./pages/Login"

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route exact path="/" element ={<Home />} />
          <Route exact path="/login" element ={<Login />} />
          <Route element={<h1 className="text-9xl"> Not Found!</h1>} />
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
