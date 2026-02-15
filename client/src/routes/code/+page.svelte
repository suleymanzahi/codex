<script>
    import CodeMirror from "svelte-codemirror-editor";
    import { python } from "@codemirror/lang-python";
    import { cobalt } from "thememirror";
    import { useAuthState, PUBLIC_WS_URL } from "$lib/authState.svelte.js";
    import { goto } from "$app/navigation";
    import { browser } from "$app/environment";

    const auth = useAuthState();

    $effect.pre(() => {
        if (browser && !auth.token) {
            goto("/login");
        }
    });

    import { Button, Modal, Label, Input, Textarea } from "flowbite-svelte";
    import { onMount } from "svelte";

    let files = $state(["main.py"]);
    let contents = $state([
        `def avg(array): \n\treturn sum(array) / len(array)\nnumbers = [1, 2, 3, 4, 5]\nprint(f"Average = {avg(numbers)}")
        `,
    ]);
    let currentTabIdx = $state(0);
    let value = $state(contents[0]);
    let result = $state("$shell:\n");

    function closeTab(idx) {
        files.splice(idx, 1);
        contents.splice(idx, 1);
        currentTabIdx = Math.max(0, currentTabIdx - 1); // 6 -> max(5, min(5,0)) -> 5, 1 -> max(5, min(5,0)) -> 5
        console.log("After close: " + currentTabIdx);
        value = contents[currentTabIdx];
    }

    let saveFileModal = $state(false);
    let error = $state("");
    const langEnd = "py";
    const fileNameRegex = new RegExp(`\\p{L}[\\p{L}\\p{N}]*\\.${langEnd}`, "u");
    function onaction({ action, data }) {
        error = "";
        const fileName = data.get("fileName");
        if (files.includes(fileName)) {
            error = "File name already exists";
            return false;
        }
        if (!fileNameRegex.test(fileName)) {
            console.log("regex");
            error = "File name must be valid (e.g., example.py)";
            return false;
        }

        files.push(fileName);
        contents.push("");
        currentTabIdx = files.length - 1;
        value = contents[currentTabIdx];
    }

    let view = $state();
    let ws;
    if (browser) {
        ws = new WebSocket(PUBLIC_WS_URL, auth.token);
        ws.addEventListener("message", (e) => {
            console.log(`Receive message: ${e.data}`);
            result = `$shell:\n${e.data}`;
        });
    }

    $inspect(value);
    $inspect(files);
    $inspect(currentTabIdx);
    $inspect(saveFileModal);
</script>

<header class="flex justify-between my-4 mx-24">
    <h1 class="text-center text-white text-3xl">Codex</h1>
    <Button
        class="bg-sky-900"
        onclick={() => {
            if (browser) {
                auth.logout();
                goto("/login");
            }
        }}
    >
        Log Out</Button
    >
</header>

<div class="w-max mx-auto">
    <div
        class="flex flex-row justify-between border-y border-gray-700 select-none max-w-[900px]"
    >
        <div
            class="flex select-none max-w-[880px] overflow-x-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
        >
            {#each files as file, i}
                <!-- svelte-ignore a11y_click_events_have_key_events -->
                <!-- svelte-ignore a11y_no_static_element_interactions -->
                <div
                    class="group flex items-center gap-2 px-4 py-2
            
            {currentTabIdx === i
                        ? 'border-b border-green-500 text-white'
                        : 'text-gray-500 hover:text-white '}"
                >
                    <span
                        class="truncate cursor-pointer"
                        onclick={() => {
                            value = contents[i];
                            currentTabIdx = i;
                        }}>{file}</span
                    >

                    {#if files.length > 1}
                        <button
                            onclick={(e) => {
                                closeTab(i);
                            }}
                            class="opacity-0 group-hover:opacity-100 hover:bg-gray-600 text-gray-300
                       rounded-sm w-4 h-4 flex items-center justify-center transition"
                        >
                            ✕
                        </button>
                    {/if}
                </div>
            {/each}
        </div>

        <button
            class="text-3xl text-gray-500 hover:text-white px-2 border-l-[0.5px] border-gray-400"
            onclick={() => (saveFileModal = true)}>+</button
        >
    </div>

    <CodeMirror
        bind:value
        onchange={(value) => (contents[currentTabIdx] = value)}
        onready={(cm_view) => (view = cm_view)}
        lang={python()}
        theme={cobalt}
        styles={{
            "&": {
                width: "900px",
                maxWidth: "100%",
                height: "25rem",
                borderRight: "1px solid black",
                borderBottom: "1px solid black",
            },
        }}
    />

    <Button
        class=" my-4 max-w-content bg-green-700 text-white "
        type="submit"
        value="create"
        onclick={() => {
            const code = {};
            const filesCopy = files.slice();
            const filesObj = filesCopy.reduce((obj, key, index) => {
                obj[key] = contents[index];
                return obj;
            }, {});
            code["files"] = filesObj;
            code["entry"] = files[currentTabIdx];
            ws.send(JSON.stringify(code));
            console.log(code);
        }}>Run</Button
    >

    <textarea
        readonly
        contenteditable="true"
        bind:innerHTML={result}
        class=" bg-black font-medium text-green-300 my-4 w-[900px] h-[200px] block resize-none rounded"
        >$shell:</textarea
    >
</div>

<!-- TODO: have to check for duplicate files, use map to store file name occurences, append count-->
<!-- TODO: add text area where code exectution output will be put-->
<!-- TODO: spin up backend, send all files with code (as JSON-object?)-->
<!-- TODO: refactor event handlers as functions-->

<Modal form bind:open={saveFileModal} size="xs" {onaction}>
    <div class="flex flex-col space-y-6">
        <h3 class="mb-4 text-xl font-medium text-white">Create New File</h3>
        {#if error}
            <Label color="red">{error}</Label>
        {/if}
        <Label class="space-y-2">
            <span>File Name</span>
            <Input class="mt-4" type="text" name="fileName" required />
        </Label>
        <div class="flex flex-row justify-end">
            <Button
                class="w-content bg-green-700 text-white"
                type="submit"
                value="create">Create</Button
            >
        </div>
    </div>
</Modal>

<style>
    :global(body) {
        margin: 0;
    }
</style>
