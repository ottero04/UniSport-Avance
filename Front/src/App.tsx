import { BrowserRouter, Routes, Route } from "react-router-dom"
import LoginPage from "./Pages/LoginPage"
import Dashboardpage from "./Pages/DashboardPage"
import RegisterPage from "./Pages/RegisterPage"
import "./App.css"

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/profile" element={<Dashboardpage />} />
        <Route path="/Registro" element={<RegisterPage />} />
      </Routes>
    </BrowserRouter>
  )

}

export default App