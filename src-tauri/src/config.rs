use serde::{Deserialize, Serialize};
use std::fs::{File, OpenOptions};
use std::io::{self, Write};
use std::path::Path;

pub struct AppConfig{
    popup_chance_min: u8,
    popup_chance_max: u8,
    popup_opacity_min: u8,
    popup_opacity_max: u8,
}

impl AppConfig {
    pub fn new() -> Self {
        Self {
            popup_chance_min: 10,
            popup_chance_max: 100,
            
            popup_opacity_min: 50,
            popup_opacity_max: 100,
        }
    }

    pub fn save(&self, file_path: &str) -> io::Result<()> {
        let file = OpenOptions::new()
            .write(true)
            .truncate(true)
            .create(true)
            .open(file_path)?;

        serde_json::to_writer_pretty(file, self)?;
        Ok(())
    }

    // Load the configuration from a file
    pub fn load(file_path: &str) -> io::Result<Self> {
        let file = File::open(file_path)?;
        let reader = io::BufReader::new(file);

        let config: Self = serde_json::from_reader(reader)?;
        Ok(config)
    }
}