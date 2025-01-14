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
use python::main::{add_cwd_to_path, read_python_main, create_lib_module};
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
                df: Arc::new(Mutex::new(DFInstance::new(process))),
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
            loop {
                let mut df = state.df.blocking_lock();
                // recreate the process instance every time to make sure it's still running. Do it after the lock so we can track its status
                let process = match win::process::Process::new_by_name(PROCESS_NAME) {
                    Ok(p) => {
                        // if the process is found update the pid
                        df.pid = p.pid;
                        p
                    },
                    Err(e) => {
                        // if the process is not found sleep for 5 seconds and try again
                        eprintln!("Update Task: {}", e);
                        df.pid = 0;
                        // drop the lock so it doesn't hold up the GUI if the process is not found
                        drop(df);
                        std::thread::sleep(Duration::from_secs(5));
                        continue
                    }
                };

                println!("Updating...");
                // TODO: add check for if the game has a loaded save,
                // if not don't try to load the dwarves
                // I think Dwarf Therapist does this by checking the year or vtable or something
                df.load_dwarves(&process);

                drop(df);
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

                // have to import the modules for the python script here to use them
                let requests = PyModule::import(py, "requests");
                let qt6 = PyModule::import(py, "PyQt6.QtWidgets");
                let app = PyModule::import(py, "app");
                let script = match read_python_main(py) {
                    Ok(script) => script,
                    Err(e) => {
                        eprintln!("Failed to read the python script:\n{}", e);
                        std::process::exit(1);
                    }
                };
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