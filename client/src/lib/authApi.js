import { env } from '$env/dynamic/public';
import { browser } from '$app/environment';

let PUBLIC_API_URL;
if (browser) {
  PUBLIC_API_URL = `http://${window.location.hostname}:${env.PUBLIC_API_PORT}`; 
}

const login = async (credentials) => {
  console.log(JSON.stringify(credentials))
  return await fetch(`${PUBLIC_API_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  });
};

const register = async (user) => {
  return await fetch(`${PUBLIC_API_URL}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(user),
  });
};

export { login, register };