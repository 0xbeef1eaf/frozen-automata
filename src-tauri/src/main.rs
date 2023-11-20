// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::{time::Duration, sync::Arc};
use tauri_plugin_store::StoreBuilder;
use uuid::Uuid;
use tauri::{async_runtime::{Mutex, spawn}, Manager, AppHandle};
use rand::Rng;

mod tray;
mod config;

fn run_loop(app_handle: AppHandle) {
    let mut rng = rand::thread_rng();
    let rand = rng.gen_range(0..100);
    
}

fn main() {
    let app = tauri::Builder::default()
        .system_tray(tray::menu())
        .on_system_tray_event(tray::system_tray_handler)
        .invoke_handler(tauri::generate_handler![])
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    let app_handle = Arc::new(Mutex::new(app.handle()));

    spawn(async move {
        loop {
            std::thread::sleep(Duration::from_secs(1));
            let local_app_handle = app_handle.clone();
            let temp = local_app_handle.lock().await.app_handle();


            let window = tauri::WindowBuilder::new(
                &temp, 
                format!("popup-{}", Uuid::new_v4()), 
                tauri::WindowUrl::App("windows/popup.html".into())
            )
                .transparent(true)
                .always_on_top(true)
                .focused(true)
                .maximizable(false)
                .minimizable(false)
                .decorations(false)
                .skip_taskbar(true)
                .resizable(false)
                .build().unwrap();
        }
    });

    app.run(|_app_handle, event| match event {
        tauri::RunEvent::ExitRequested { api, .. } => {
          api.prevent_exit();
        }
        _ => {}});
}
