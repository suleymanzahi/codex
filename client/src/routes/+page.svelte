<script>
    import { useAuthState } from "$lib/authState.svelte.js";
    import { goto } from "$app/navigation";
    import { browser } from "$app/environment";
    import { Button, Modal, Label, Input, Textarea } from "flowbite-svelte";

    const auth = useAuthState();
</script>

<h1 class="text-center text-white text-6xl mt-2 mb-8">Welcome to Codex</h1>

<div class="flex flex-col items-center justify-center">
    <h3 class="text-white text-2xl mt-2 mb-8">
        Your new Python code editor in the browser
    </h3>

    <Button
        class="bg-green-900"
        onclick={() => {
            if (browser) {
                if (auth.token) {
                    goto("/code");
                } else {
                    goto("/login");
                }
            }
        }}>Start now</Button
    >
</div>
