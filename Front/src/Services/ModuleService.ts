export const getModules = async () => {
  const response = await fetch("http://localhost:5000/modules")

  if (!response.ok) {
    throw new Error("Error cargando módulos")
  }

  return await response.json()
}