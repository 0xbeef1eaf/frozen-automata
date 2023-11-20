use tauri::{SystemTrayMenu, AppHandle, SystemTrayEvent, SystemTray, CustomMenuItem, SystemTrayMenuItem, Manager};

pub fn system_tray_handler (
    app: &AppHandle,
    event: SystemTrayEvent,
) {
    match event {
        SystemTrayEvent::MenuItemClick { id, .. } => {
            match id.as_str() {
                "config" => {
                }
                "quit" => {
                    let windows = app.windows();
                    for window in windows {
                        window.1.close().unwrap();
                    }
                    std::process::exit(0);
                }
                _ => {}
            }
        }
        _ => {}
    }
}

pub fn menu () -> SystemTray {
    SystemTray::new()
        .with_menu(
            SystemTrayMenu::new()
                .add_item(
                    CustomMenuItem::new("config".to_string(), "Config")
                )
                .add_native_item(SystemTrayMenuItem::Separator)
                .add_item(
                    CustomMenuItem::new("quit".to_string(), "Quit")
                )
        )
}

