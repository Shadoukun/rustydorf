#![allow(unused_imports)]
#![allow(unused_variables)]
mod api;
mod attribute;
mod dfinstance;
mod dwarf;
mod caste;
mod thought;
mod flagarray;
mod language;
mod logger;
mod need;
mod win;
mod histfigure;
mod skill;
mod squad;
mod time;
mod syndromes;
mod items;
mod preference;
mod data;
mod race;
mod util;
mod python;

use log::{info, warn, error};
use logger::init_logger;
use std::{sync::Arc, time::Duration};
use axum::{routing::get, Router};
use python::main::{add_cwd_to_path, read_python_main, create_lib_module};
use tokio::sync::Mutex;

use pyo3::prelude::*;

use dfinstance::DFInstance;
use api::{AppState, get_dwarves_handler, get_gamedata_handler};

const PROCESS_NAME: &str = "Dwarf Fortress.exe";

#[tokio::main]
async fn main() {

    init_logger(log::LevelFilter::Debug).unwrap();

    pyo3::prepare_freethreaded_python();

    unsafe {
        let state = {
            let process = win::process::Process::new_by_name(PROCESS_NAME);
            AppState {
                df: Arc::new(Mutex::new(DFInstance::new(process))),
            }
        };

        // Spawn the REST API server for communication with the GUI
        let api_server = tokio::spawn({
            info!("Starting API server...");
            let state = state.clone();
            async move {
                let rest = Router::new()
                    .route("/data", get(get_gamedata_handler))
                    .route("/dwarves", get(get_dwarves_handler))
                    .with_state(state);

                let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
                axum::serve(listener, rest).await.unwrap();
            }
        });

        /* Periodically updates the DFInstance by monitoring the Dwarf Fortress process,
        loading game data if not already loaded, and fetching the latest list of dwarves.
        This task runs in a loop, ensuring the application state remains current by
        handling process monitoring and data refreshes at specified intervals. */
        let update_task = tokio::task::spawn_blocking(move || {
            info!("Starting update task...");
            loop {
                info!("Update Task | Checking for Dwarf Fortress process...");
                let mut df = state.df.blocking_lock();

                // recreate the process instance every time to make sure it's still running. Do it after the lock so we can track its status
                let process = match win::process::Process::new_by_name(PROCESS_NAME) {
                    Ok(p) => {
                        // if the process is found update the pid
                        df.pid = p.pid;
                        p
                    },
                    Err(e) => {
                        error!("Update Task | failed to find process: {}", e);
                        df.pid = 0;
                        // drop the lock so it doesn't hold up the GUI if the process is not found
                        drop(df);
                        std::thread::sleep(Duration::from_secs(5));
                        continue
                    }
                };

                info!("Update Task | Process found, loading data...");
                match df.load_data(&process) {
                    Ok(_) => {
                        info!("Update Task | Data loaded successfully");
                        match df.load_dwarves(&process) {
                            Ok(_) => {info!("Update Task | Dwarves loaded successfully");},
                            Err(e) => {
                                error!("Update Task | load_dwarves | {}", e);
                                drop(df);
                                std::thread::sleep(Duration::from_secs(5));
                                continue
                            }
                        }
                        drop(df);
                        std::thread::sleep(Duration::from_secs(30));
                    },
                    Err(e) => {
                        error!("Update Task | load_data | {}", e);

                        // check for embark screen if the data failed to load
                        info!("Update Task | Checking for embark screen...");
                        if df.is_on_embark_screen(&process) {
                            info!("Update Task | Embark screen detected, Trying to load data again...");
                            match df.load_dwarves(&process) {
                                Ok(_) => {info!("Update Task | Dwarves loaded successfully");},
                                Err(e) => {
                                    error!("Update Task | load_dwarves | {}", e);
                                    drop(df);
                                    std::thread::sleep(Duration::from_secs(5));
                                    continue
                                }
                            }
                        }
                        drop(df);
                        std::thread::sleep(Duration::from_secs(5));
                        continue
                    }
                }
            }
        });

        /* Spawns a new thread to run the GUI. This thread is responsible for initializing the Python interpreter,
        adding the current directory to the Python path, adding the relevant Rust code as a python module,
        and running the main Python script. */
        let gui_thread = tokio::task::spawn_blocking(move || {
            info!("Starting GUI thread...");
            info!("GUI Thread | Initializing Python interpreter...");
            Python::with_gil(|py| {
                match add_cwd_to_path(py) {
                    Ok(_) => (),
                    Err(e) => {
                        error!("GUI Thread | Failed to add current directory to Python path:\n{}", e);
                        std::process::exit(1);
                    }
                }

                info!("GUI Thread | Creating Rust module in Python...");
                match create_lib_module(py) {
                    Ok(_) => (),
                    Err(e) => {
                        error!("GUI Thread | Failed to create Rust module in Python:\n{}", e);
                        std::process::exit(1);
                    }
                }

                info!("GUI Thread | Running main Python script...");
                // we have to import the modules for the python script here to use them
                let requests = PyModule::import(py, "requests");
                let qt6 = PyModule::import(py, "PyQt6.QtWidgets");
                let app = PyModule::import(py, "app");
                let script = match read_python_main(py) {
                    Ok(script) => script,
                    Err(e) => {
                        error!("GUI Thread | Failed to read the main python script:\n{}", e);
                        std::process::exit(1);
                    }
                };

                match script.getattr("main").unwrap().call0() {
                    Ok(_) => (),
                    Err(e) => {
                        error!("GUI Thread | Failed to execute the main python script:\n{}", e);
                        std::process::exit(1);
                    }
                }
            });
        });

        tokio::select! {
            _ = api_server => {},
            _ = update_task => {},
            _ = gui_thread => {},
            _ = tokio::signal::ctrl_c() => {
                println!("Shutting down...");
            },
        }
    }
}