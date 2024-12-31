pub mod python {
    use std::{ffi::CString, fs, path::Path};

    use pyo3::prelude::*;
    use super::rustworker::RustWorker;

/// This is the python "script" that is run by the Rust program
    pub fn run_python_main(py: Python<'_>) -> Result<(), pyo3::PyErr> {
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

        // Load the Python script as a module
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

        // Call the main function in the Python script
        let _ = module.getattr("main").unwrap().call0().expect("Failed to call the function");
        Ok::<(), pyo3::PyErr>(())
    }

    pub fn create_lib_module(py: Python) -> PyResult<()> {
        let rust_module = PyModule::new(py, "rustlib")?;
        rust_module.add_class::<RustWorker>()?;
        py.import("sys")?
            .getattr("modules")?
            .set_item("rustlib", rust_module)?;
        Ok(())
    }
}

pub mod rustworker {
    use pyo3::prelude::*;
    use std::thread;
    use std::time::Duration;
    use std::sync::Arc;
    use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

    #[pyclass]
    /// This class is exposed to Python and is used to start and stop a Rust worker thread.
    pub struct RustWorker {
        running: Arc<AtomicBool>,
        sleep_time: Arc<AtomicU64>,
    }

    #[pymethods]
    impl RustWorker {
        #[new]
        /// Create a new RustWorker instance
        pub fn new() -> Self {
            RustWorker {
                running: Arc::new(AtomicBool::new(false)),
                sleep_time: Arc::new(AtomicU64::new(10)),
            }
        }

        /// Start the worker thread
        pub fn start(&mut self, _py: Python, callable: PyObject, sleep: u64) -> PyResult<()> {
            let running = self.running.clone();
            let sleep_time = self.sleep_time.clone();

            // Set the running flag to true
            running.store(true, Ordering::SeqCst);
            // Set the sleep time
            sleep_time.store(sleep, Ordering::SeqCst);

            // idk if I should be doing spawn_blocking, or tokio at all, but it works.
            tokio::task::spawn_blocking(move || {
                // loop until the running flag is set to false
                while running.load(Ordering::SeqCst) {
                    // Call the Python function
                    Python::with_gil(|py| {
                        let res = callable.call1(py, ());
                        match res {
                            Ok(_) => (),
                            Err(e) => eprintln!("Error calling Python function: {:?}", e),
                        }
                    });
                    // Sleep
                    thread::sleep(Duration::from_secs(sleep_time.load(Ordering::SeqCst)));

                }
            });
            Ok(())
        }

        /// Stop the worker thread
        pub fn stop(&mut self) {
            // Set the running flag to false
            self.running.store(false, Ordering::SeqCst);
        }

        /// Set the sleep time for the worker thread
        /// The sleep time is in seconds
        pub fn set_sleep_time(&mut self, sleep_time: u64) {
            self.sleep_time.store(sleep_time, Ordering::SeqCst);
        }
    }
}