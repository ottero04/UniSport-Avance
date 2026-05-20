import Dashboard from "../Components/Dashboard"
import Menu from "../Components/Menu"
import "./DashboardPage.css"

function Dashboardpage() {
  return (
    <div className="dashboard-layout">
      <Menu />
      <Dashboard />
    </div>
  )
}

export default Dashboardpage