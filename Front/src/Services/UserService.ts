export const getUser = async (id: number) => {
    const response = await fetch(`http://localhost:5000/usuario/${id}`)

    const data = await response.json()

    if (!response.ok) {
        throw new Error(data.error || "Error obteniendo usuario")
    }
    console.log("RESPUESTA BACKEND USER:", data);
    return data
}