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

use std::{sync::Arc, time::Duration};
use axum::{routing::get, Router};
use python::main::{add_cwd_to_path, read_script, create_lib_module};
use tokio::sync::Mutex;

use pyo3::prelude::*;

use dfinstance::DFInstance;
use api::{AppState, get_dwarves_handler, get_gamedata_handler};

const PROCESS_NAME: &str = "Dwarf Fortress.exe";

#[tokio::main]
async fn main() {

    pyo3::prepare_freethreaded_python();

    unsafe {
        // create the AppState for the REST API
        let state = {
            let process = win::process::Process::new_by_name(PROCESS_NAME);
            AppState {
                df: Arc::new(Mutex::new(DFInstance::new(&process))),
            }
        };

        let api_server = tokio::spawn({
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

        // start the update task
        let update_task = tokio::task::spawn_blocking(move || {
            // process can't be sent between threads, so we need to create a new one here
            let process = win::process::Process::new_by_name(PROCESS_NAME);
            loop {
                // this is its own scope so that the mutex lock is dropped before the sleep
                {
                    let mut df = state.df.blocking_lock();
                    df.load_dwarves(&process);
                    println!("Updating...");
                }
                std::thread::sleep(Duration::from_secs(30));
            }
        });

        // start the python GUI thread
        let gui_thread = tokio::task::spawn_blocking(move || {
            Python::with_gil(|py| {
                match add_cwd_to_path(py) {
                    Ok(_) => (),
                    Err(e) => {
                        eprintln!("Failed to add the current directory to the Python path:\n{}", e);
                        std::process::exit(1);
                    }
                }

                match create_lib_module(py) {
                    Ok(_) => (),
                    Err(e) => {
                        eprintln!("Failed to create the Rust module in Python:\n{}", e);
                        std::process::exit(1);
                    }
                }

                let requests = PyModule::import(py, "requests");
                let qt6 = PyModule::import(py, "PyQt6.QtWidgets");
                let app = PyModule::import(py, "app");
                let script = read_script(py).unwrap();
                script.getattr("main").unwrap().call0().expect("Failed to call the python script");
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