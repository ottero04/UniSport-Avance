export const login = async (nickname: string, password: string) => {
  const response = await fetch("http://localhost:5000/usuario/auth", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      nickname: nickname,
      password_hash: password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Error en login");
  }

  return data;
};

export const register = async (
  nombre: string,
  nickname: string,
  correo: string,
  telefono: string,
  password_hash: string,
  identificacion: string
) => {
  const response = await fetch("http://localhost:5000/registro", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      nombre,
      nickname,
      correo,
      telefono,
      password_hash,
      identificacion,
    }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Error en el registro");
  }
  return data;
};