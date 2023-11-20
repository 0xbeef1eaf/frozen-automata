import { invoke } from "@tauri-apps/api/tauri";

async function get_media(type: string) {
  let media = await invoke('get_media', {
    type: type
  })
  document.getElementById('media')?.setAttribute('src', media as string)
}

window.addEventListener("DOMContentLoaded", () => {

});
