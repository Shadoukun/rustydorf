use std::ffi::CStr;
use std::mem::size_of;
use std::ptr::null_mut;
use winapi::um::tlhelp32::{CreateToolhelp32Snapshot, Module32First, Process32First, Process32Next, MODULEENTRY32, PROCESSENTRY32, TH32CS_SNAPMODULE, TH32CS_SNAPPROCESS};
use winapi::um::processthreadsapi::OpenProcess;
use winapi::um::handleapi::{CloseHandle, INVALID_HANDLE_VALUE};
use winapi::um::winnt::PROCESS_ALL_ACCESS;
use winapi::shared::minwindef::{FALSE, TRUE};
use winapi::shared::ntdef::HANDLE;

#[derive(Clone)]
pub struct Process {
    pub pid: u32,
    pub handle: HANDLE,
    pub modules: Vec<MODULEENTRY32>,
}

impl Default for Process {
    fn default() -> Self {
        Process {
            pid: 0,
            handle: null_mut(),
            modules: Vec::new(),
        }
    }
}

impl Process {
    pub unsafe fn new(pid: u32, handle: HANDLE) -> Self {
        let mut proc = Process {
            pid,
            handle,
            modules: Vec::new(),
        };
        proc.create_module_snapshot();
        proc
    }

    pub unsafe fn new_by_name(target_process_name: &str) -> Self {
        let mut pe32: PROCESSENTRY32 = std::mem::zeroed();
        pe32.dwSize = size_of::<PROCESSENTRY32>() as u32;

        // Create a snapshot of all processes
        let proc_snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if proc_snapshot == INVALID_HANDLE_VALUE {
            panic!("Failed to create process snapshot.");
        }

        // Get the first process
        if Process32First(proc_snapshot, &mut pe32) == FALSE {
            panic!("Failed to get the first process.");
        }

        loop {
            // Check if the process name matches the target process name
            let cur_process_name = CStr::from_ptr(pe32.szExeFile.as_ptr()).to_string_lossy();
            if cur_process_name.to_lowercase() == target_process_name.to_lowercase() {
                let proc_h: HANDLE = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pe32.th32ProcessID);
                if proc_h.is_null() {
                    panic!("Failed to open process.");
                }
                return Process::new(pe32.th32ProcessID, proc_h);
            }

            // Get the next process
            if Process32Next(proc_snapshot, &mut pe32) == FALSE {
                break;
            }
        }

        panic!("Process not found.");
    }

    unsafe fn create_module_snapshot(&mut self) {
        // Create a snapshot of the process's modules
        let handle: HANDLE = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, self.pid);
        if handle == INVALID_HANDLE_VALUE {
            panic!("Failed to create module snapshot.");
        }

        let mut me32: MODULEENTRY32 = std::mem::zeroed();
        me32.dwSize = size_of::<MODULEENTRY32>() as u32;
        if Module32First(handle, &mut me32) == FALSE {
            panic!("Failed to get the first module.");
        }

        self.modules.push(me32);
    }
}

impl Drop for Process {
    fn drop(&mut self) {
        unsafe {
            CloseHandle(self.handle);
        }
    }
}