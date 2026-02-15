import * as authApi from "$lib/authApi.js";
import { env } from '$env/dynamic/public';
import { browser } from '$app/environment';

const USER_KEY = "user";
const TOKEN_KEY = "token";
let PUBLIC_WS_URL; 
if (browser) {
  PUBLIC_WS_URL = `ws://${window.location.hostname}:${env.PUBLIC_API_PORT}/ws`;
}

let user = $state(null);
let token = $state(null);

if (browser) {
  const storedUser = localStorage.getItem(USER_KEY);
  const storedToken = localStorage.getItem(TOKEN_KEY);

  if (storedUser) {
    user = storedUser;
  }
  if (storedToken) {
    token = storedToken;
  }
}

const useAuthState = () => {
  return {
    get user() {
      return user;
    },
    get token() {
      return token;
    },
    login: async (username, password) => {
      const response = await authApi.login({ username, password });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Login failed");
      }

      const data = await response.json();
      user = data.user;
      token = data.token;

      localStorage.setItem("user", data.user);
      localStorage.setItem("token", data.token);

      return data;
    },
    register: async (username, password) => {
      const response = await authApi.register({ username, password });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Registration failed");
      }

      return await response.json();
    },
    logout: () => {
      user = null;
      token = null;

      localStorage.removeItem("user");
      localStorage.removeItem("token");
    },
  };
};

export { useAuthState, PUBLIC_WS_URL };