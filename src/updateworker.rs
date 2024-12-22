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
            sleep_time: Arc::new(AtomicU64::new(60)),
        }
    }

    /// Start the worker thread
    pub fn start(&mut self, _py: Python, callable: PyObject) -> PyResult<()> {
        let running = self.running.clone();
        let sleep_time = self.sleep_time.clone();

        // Set the running flag to true
        running.store(true, Ordering::SeqCst);

        thread::spawn(move || {
            // loop until the running flag is set to false
            while running.load(Ordering::SeqCst) {
                // Call the Python function
                Python::with_gil(|py| {
                    let _ = callable.call1(py, ());
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

#[pymodule]
fn rust_worker(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustWorker>()?;
    Ok(())
}