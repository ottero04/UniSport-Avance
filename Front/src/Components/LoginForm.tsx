import { useState } from "react"
import { useNavigate } from "react-router-dom"
import logo from "../assets/sin fondo.jpeg"
import { login } from "../Services/AuthService"

function LoginForm() {

    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const navigate = useNavigate()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        try {
            const data = await login(username, password)

            alert("Login correcto")
            
            console.log(data)

            // guardar usuario
            localStorage.setItem("usuario", JSON.stringify(data.usuario))
            navigate("/profile")

        } catch (error: any) {
            alert(error.message)
        }
    }

    return (
        <div className="login-container">

            <h2>UniSport</h2>
            <img src={logo} alt="Uni Sport Logo" className="logo" />

            <form onSubmit={handleSubmit}>

                <input
                    type="text"
                    placeholder="Usuario"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />

                <input
                    type="password"
                    placeholder="Contraseña"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button type="submit">
                    Iniciar sesión
                </button>

            </form>

            <p style={{ color: "#aaa", fontSize: "14px", marginTop: "16px" }}>
                ¿No tienes cuenta?{" "}
                <span
                    onClick={() => window.location.href = "/Registro"}
                    style={{ color: "#f5b700", cursor: "pointer", fontWeight: "bold" }}
                >
                    Regístrate
                </span>
            </p>

        </div>
    )
}

export default LoginForm