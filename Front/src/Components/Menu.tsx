import { useEffect, useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import logo from "../assets/sin fondo.jpeg"
import "./Menu.css"

interface Module {
  id: number
  description: string
  route: string
  status: number
}

function Menu() {
  const [collapsed, setCollapsed] = useState(false)
  const [modules, setModules] = useState<Module[]>([])
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    fetch("http://localhost:5000/modules")
      .then(res => res.json())
      .then(data => setModules(data))
      .catch(err => console.error("Error modules:", err))
  }, [])

  const handleNavigate = (route: string) => {
    navigate(route)
  }

  return (
    <div className={`menu ${collapsed ? "collapsed" : ""}`}>

      
      <div className="menu-header">
        <button
          className="menu-toggle"
          onClick={() => setCollapsed(!collapsed)}
        >
          ☰
        </button>

        <img src={logo} alt="Uni Sport Logo" className="logo" />



      </div>

      
      <div className="menu-items">
        {modules.map((mod) => {
          const isActive = location.pathname === mod.route
          return (
            <div
              key={mod.id}
              onClick={() => navigate(mod.route)}
              className={`menu-item ${isActive ? "active" : ""}`}
            >
              {!collapsed && mod.description}
            </div>
          )
        })}
      </div>

    </div>
  )
}

export default Menu