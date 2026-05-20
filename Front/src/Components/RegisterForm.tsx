import { useState } from "react"
import { useNavigate } from "react-router-dom"
import logo from "../assets/sin fondo.jpeg"
import "./Registro.css"
import { register } from "../Services/AuthService"

function RegisterForm() {

    const navigate = useNavigate()

    const [form, setForm] = useState({
        nombres: "",
        apellidos: "",
        identificacion: "",
        correo: "",
        confirmarCorreo: "",
        telefono: "",
        password: "",
        confirmarPassword: "",
    })

    const [errors, setErrors] = useState<Record<string, string>>({})

    const validate = (): Record<string, string> => {
        const e: Record<string, string> = {}
        if (form.nombres.trim().length < 2)
            e.nombres = "Ingresa tus nombres."
        if (form.apellidos.trim().length < 2)
            e.apellidos = "Ingresa tus apellidos."
        if (form.identificacion.trim().length < 4)
            e.identificacion = "Ingresa un número de identificación válido."
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.correo))
            e.correo = "Ingresa un correo electrónico válido."
        if (form.confirmarCorreo !== form.correo)
            e.confirmarCorreo = "Los correos no coinciden."
        if (form.telefono.trim().length < 7)
            e.telefono = "Ingresa un número de teléfono válido."
        if (form.password.length < 6)
            e.password = "La contraseña debe tener al menos 6 caracteres."
        if (form.confirmarPassword !== form.password)
            e.confirmarPassword = "Las contraseñas no coinciden."
        return e
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target
        setForm(prev => ({ ...prev, [name]: value }))
        if (errors[name]) setErrors(prev => ({ ...prev, [name]: "" }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        const localErrors = validate()
        if (Object.keys(localErrors).length > 0) {
            setErrors(localErrors)
            return
        }
        try {
            await register(
                form.nombres + " " + form.apellidos,
                form.nombres,
                form.correo,
                form.telefono,
                form.password,
                form.identificacion
            )
            alert("¡Registro exitoso! Ahora puedes iniciar sesión.")
            navigate("/")
        } catch (error: any) {
            alert(error.message)
        }
    }

    return (
        <div className="register-container">

            <img src={logo} alt="UniSport Logo" className="logo" />
            <h2>Registro de Nuevo Usuario</h2>

            <form onSubmit={handleSubmit}>
                <div className="register-grid">

                    <div className="register-field">
                        <label className="register-label">Nombres</label>
                        <input type="text" name="nombres" placeholder="Nombres"
                            value={form.nombres} onChange={handleChange} />
                        {errors.nombres && <span className="register-error">{errors.nombres}</span>}
                    </div>

                    <div className="register-field">
                        <label className="register-label">Apellidos</label>
                        <input type="text" name="apellidos" placeholder="Apellidos"
                            value={form.apellidos} onChange={handleChange} />
                        {errors.apellidos && <span className="register-error">{errors.apellidos}</span>}
                    </div>

                    <div className="register-field">
                        <label className="register-label">Número de Identificación</label>
                        <input type="text" name="identificacion" placeholder="Número de Identificación"
                            value={form.identificacion} onChange={handleChange} />
                        {errors.identificacion && <span className="register-error">{errors.identificacion}</span>}
                    </div>

                    <div className="register-field">
                        <label className="register-label">Teléfono</label>
                        <input type="text" name="telefono" placeholder="Teléfono"
                            value={form.telefono} onChange={handleChange} />
                        {errors.telefono && <span className="register-error">{errors.telefono}</span>}
                    </div>

                    <div className="register-field">
                        <label className="register-label">Correo Electrónico</label>
                        <input type="email" name="correo" placeholder="Correo Electrónico"
                            value={form.correo} onChange={handleChange} />
                        {errors.correo && <span className="register-error">{errors.correo}</span>}
                    </div>

                    <div className="register-field">
                        <label className="register-label">Confirmar Correo</label>
                        <input type="email" name="confirmarCorreo" placeholder="Confirmar Correo"
                            value={form.confirmarCorreo} onChange={handleChange} />
                        {errors.confirmarCorreo && <span className="register-error">{errors.confirmarCorreo}</span>}
                    </div>

                    <div className="register-field">
                        <label className="register-label">Contraseña</label>
                        <input type="password" name="password" placeholder="Contraseña"
                            value={form.password} onChange={handleChange} />
                        {errors.password && <span className="register-error">{errors.password}</span>}
                    </div>

                    <div className="register-field">
                        <label className="register-label">Confirmar Contraseña</label>
                        <input type="password" name="confirmarPassword" placeholder="Confirmar Contraseña"
                            value={form.confirmarPassword} onChange={handleChange} />
                        {errors.confirmarPassword && <span className="register-error">{errors.confirmarPassword}</span>}
                    </div>

                </div>

                <button type="submit">Crear Cuenta</button>

            </form>

            <p className="register-link">
                ¿Ya tienes cuenta?{" "}
                <span onClick={() => navigate("/")}>Inicia sesión</span>
            </p>

        </div>
    )
}

export default RegisterForm