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
use python::python::run_python_main;
use tokio::sync::Mutex;
use pyo3::prelude::*;

use dfinstance::DFInstance;
use api::{AppState, get_dwarves_handler, get_gamedata_handler};

const PROCESS_NAME: &str = "Dwarf Fortress.exe";

#[tokio::main]
async fn main() {

    pyo3::prepare_freethreaded_python();

    unsafe {
        let state = {
            let process = win::process::Process::new_by_name(PROCESS_NAME);
            AppState {
                df: Arc::new(Mutex::new(DFInstance::new(&process))),
            }
        };

        let server = tokio::spawn({
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

        let python = tokio::task::spawn_blocking(move || {
            let _ = Python::with_gil(|py| {
                run_python_main(py)
            });
        });

        tokio::select! {
            _ = server => {},
            _ = update_task => {},
            _ = python => {},
            _ = tokio::signal::ctrl_c() => {
                println!("Shutting down...");
            },
        }
    }
}