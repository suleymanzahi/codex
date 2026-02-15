<script lang="ts">
    import { goto } from "$app/navigation";
    import { useAuthState } from "$lib/authState.svelte.js";

    let message = $state("");
    let errorMessage = $state("");
    let isLoading = $state(false);

    const authState = useAuthState();

    const handleForm = async (e) => {
        e.preventDefault();
        errorMessage = "";
        message = "";
        isLoading = true;

        const formData = new FormData(e.target);
        console.dir(formData);
        const { username, password } = Object.fromEntries(formData);
    
        try {
            await authState.register(username, password);
            message = "Register successful! Redirecting to login page";
            setTimeout(() => goto("/login"), 1000);
        } catch (error) {
            errorMessage = error.message;
        } finally {
            isLoading = false;
        }
    };
</script>

<header class="text-center py-4">
    <h1 class="text-4xl font-bold text-white">Register</h1>
</header>

{#if message}
  <div>
    <p class="text-white text-center m-4 p-8">{message}</p>
  </div>
{/if}

{#if errorMessage}
  <div>
    <p class="text-red-500 text-center m-4 p-8">{errorMessage}</p>
  </div>
{/if}


<p class="text-center text-white p-4">Create a new account for Codex</p>

<div class="flex justify-center">
    <form onsubmit={handleForm} class="bg-gray-800 p-4 rounded-xl shadow-lg w-80">
        <label class="text-white block mb-2" for="username">Username</label>
        <input
            id="username"
            type="text"
            name="username"
            class="w-full p-2 mb-4 rounded bg-gray-700 text-white focus:outline-none"
            required
        />

        <label class="text-white block mb-2" for="password">Password</label>
        <input
            id="password"
            type="password"
            name="password"
            class="w-full p-2 mb-6 rounded bg-gray-700 text-white focus:outline-none"
            required
        />

        <div class="flex justify-center">
             <button
            type="submit"
            class="w-16  bg-blue-600 hover:bg-blue-700 text-white py-2 rounded transition mb-2"
            
        >
            Submit
        </button>

        </div>

        <p class="  text-xs text-center text-white">Already signed up? Login <a class="underline" href="/login">here</a></p>
       
    </form>
</div>
