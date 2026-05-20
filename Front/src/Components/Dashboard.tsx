import { useEffect, useState } from "react"
import { getUser } from "../Services/UserService"
import userPic from "../assets/user.png"
import "./Dashboard.css"


function DashboardForm() {
    const [user, setUser] = useState<any>(null)

    useEffect(() => {
        const stored = localStorage.getItem("usuario")

        if (stored) {
            const parsed = JSON.parse(stored)
            console.log("user::", parsed)
            getUser(parsed.id)
                .then(setUser)
                .catch(console.error)
        }

    }, [])
    useEffect(() => {
        console.log("user seteado:", user);
    }, [user]);
    return (
        <div style={{ width: "90%" }}>
            <div style={{ padding: "20px" }}>
                <div className="container">

                    <div className="columns">

                        <div className="userItem">
                            <div style={{ padding: "20px", width: "70%" }}>
                                <h1 style={{ color: " color: #c7a110;" }}>Mi Perfil</h1>
                            </div>
                            <div className="userData">
                                {user ? (
                                    <>
                                        <p>Nombre: {user?.[0]?.[0]}</p>
                                        <p>Nickname: {user?.[0]?.[1]}</p>
                                        <p>Correo: {user?.[0]?.[2]}</p>
                                        <p>Telefono: {user?.[0]?.[3]}</p>
                                        <p>Saldo: {user?.[0]?.[4]}</p>
                                    </>
                                ) : (
                                    <p>Cargando usuario...</p>
                                )}
                            </div>

                        </div>
                        <div className="userIlustration">
                            <img src={userPic} alt="user logo" className="userIcon" />
                        </div>

                    </div>


                </div>
            </div>
        </div>
    )
}

export default DashboardForm