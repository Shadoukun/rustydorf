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

use std::{ffi::CString, fs, path::Path, sync::Arc, time::Duration};
use axum::{routing::get, Router};
use tokio::sync::Mutex;
use pyo3::prelude::*;

use python::rustworker::RustWorker;

use dfinstance::DFInstance;
use api::{AppState, get_dwarves_handler, get_gamedata_handler};

const PROCESS_NAME: &str = "Dwarf Fortress.exe";

pub fn create_lib_module(py: Python) -> PyResult<()> {
    let rust_module = PyModule::new(py, "rustlib")?;
    rust_module.add_class::<RustWorker>()?;
    py.import("sys")?
        .getattr("modules")?
        .set_item("rustlib", rust_module)?;
    Ok(())
}

#[tokio::main]
async fn main() {
    unsafe {
        let state = {
            let process = win::process::Process::new_by_name(PROCESS_NAME);
            AppState {
                df: Arc::new(Mutex::new(DFInstance::new(&process))),
            }
        };
        pyo3::prepare_freethreaded_python();

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

        let handle = tokio::task::spawn_blocking(move || {
            let py_result = Python::with_gil(|py| {
                let sys = PyModule::import(py, "sys").unwrap();
                let path = sys.getattr("path").unwrap();
                let binding = std::env::current_dir().unwrap();
                let current_path = binding.to_str().unwrap();
                path.call_method1("append", (current_path,)).unwrap();
                path.call_method1("append", ("venv\\Lib\\site-packages",)).unwrap();

                let requests = PyModule::import(py, "requests");
                let qt6 = PyModule::import(py, "PyQt6.QtWidgets");
                let module = PyModule::import(py, "app");

                // Create a new module and add the RustWorker class to it
                create_lib_module(py).unwrap();

                let script_path = Path::new("main.py");
                if !script_path.exists() {
                    eprintln!("Error: script.py not found in the current directory");
                    std::process::exit(1);
                }

                let script_content = fs::read_to_string(script_path)
                    .expect("Failed to read the Python script");

                let script_content_cstr = CString::new(script_content).expect("Failed to convert script content to CString");
                let file_name = &CString::new("main.py").unwrap();
                let module_name = &CString::new("app").unwrap();

                let module = PyModule::from_code(py,
                    script_content_cstr.as_c_str(),
                    file_name,
                    module_name
                    ).expect("Failed to load the Python script as a module");

                let result = module.getattr("main").expect("Failed to get the function");
                let value = result.call0().expect("Failed to call the function");
                Ok::<(), pyo3::PyErr>(())
            });
        });

        tokio::select! {
            _ = server => {},
            _ = update_task => {},
            _ = handle => {},
            _ = tokio::signal::ctrl_c() => {
                println!("Shutting down...");
            },
        }
    }
}
