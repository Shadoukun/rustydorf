use pyo3::prelude::*;
use std::thread;
use std::time::Duration;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

#[pyclass]
pub struct UpdateWorker {
    running: Arc<AtomicBool>,
}

#[pymethods]
impl UpdateWorker {
    #[new]
    pub fn new() -> Self {
        UpdateWorker {
            running: Arc::new(AtomicBool::new(false)),
        }
    }

    /// This will be called from python to start the worker thread.
    pub fn start(&mut self, _py: Python, callable: PyObject) -> PyResult<()> {
        let running = self.running.clone();
        running.store(true, Ordering::SeqCst);

        thread::spawn(move || {
            while running.load(Ordering::SeqCst) {
                Python::with_gil(|py| {
                    let _ = callable.call1(py, ());
                });

                thread::sleep(Duration::from_secs(1));
            }
        });

        Ok(())
    }

    pub fn stop(&mut self) {
        self.running.store(false, Ordering::SeqCst);
    }
}

#[pymodule]
fn update_worker(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<UpdateWorker>()?;
    Ok(())
}