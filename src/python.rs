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

            tokio::task::spawn_blocking(move || {
                // loop until the running flag is set to false
                while running.load(Ordering::SeqCst) {
                    // Call the Python function
                    Python::with_gil(|py| {
                        println!("Calling Python function");
                        let res = callable.call1(py, ());
                        match res {
                            Ok(_) => println!("Python function called successfully"),
                            Err(e) => println!("Error calling Python function: {:?}", e),
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
