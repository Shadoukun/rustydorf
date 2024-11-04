use std::ffi::CStr;

use windows::Win32::System::Diagnostics::ToolHelp::{CreateToolhelp32Snapshot, Module32First, Process32First, Process32Next, MODULEENTRY32, PROCESSENTRY32, TH32CS_SNAPMODULE, TH32CS_SNAPPROCESS};
use windows::Win32::System::Threading::{OpenProcess, PROCESS_ALL_ACCESS};
use windows::Win32::Foundation::{CloseHandle, HANDLE};

#[derive(Default)]
pub struct Process {
    pub pid: u32,
    pub handle: HANDLE,
    pub modules: Vec<MODULEENTRY32>,
}

impl Process {
    pub unsafe fn new(pid: u32, handle: HANDLE) -> Self {
        let mut proc = Process {
            pid,
            handle,
            modules: Vec::new(),
        };
        proc.create_module_snapshot();
        return proc;
    }

    pub unsafe fn new_by_name(target_process_name: &str) -> Self {
        let mut pe32: PROCESSENTRY32 = Default::default();
        pe32.dwSize = size_of::<PROCESSENTRY32>() as u32;

        // Create a snapshot of all processes
        // th32ProcessID is 0, so the snapshot is of all processes
        // TH32CS_SNAPPROCESS is the flag to get a snapshot of all processes
        let proc_snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,  0).unwrap_or_else(|e| {
            panic!("Failed to create process snapshot. Error: {}", e);
        });

        // Get the first process
        let _ = Process32First(proc_snapshot, &mut pe32);
        loop {
            // Check if the process name matches the target process name
            let cur_process_name = CStr::from_ptr(pe32.szExeFile.as_ptr()).to_string_lossy();
            if cur_process_name.to_lowercase() == target_process_name.to_lowercase() {
                let proc_h: HANDLE = OpenProcess(PROCESS_ALL_ACCESS, false, pe32.th32ProcessID).unwrap();
                return Process::new(pe32.th32ProcessID, proc_h);
            }

            // Get the next process
            pe32.szExeFile = [0;260];
            let _ = Process32Next(proc_snapshot, &mut pe32);
        }
    }

   unsafe fn create_module_snapshot(&mut self) {
        // Create a snapshot of the process's modules
        let handle: HANDLE = match CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, self.pid) {
            Ok(x) => x,
            Err(e) => {
                panic!("Failed to create module snapshot. Error: {}", e);
            },
        };

        let mut me32: MODULEENTRY32 = MODULEENTRY32::default();
        me32.dwSize = size_of::<MODULEENTRY32>() as u32;
        match Module32First(handle, &mut me32) {
            Ok(x) => x,
            Err(e) => panic!("Failed to create module snapshot. {}", e)
        };

        self.modules.push(me32);
    }
}

impl Drop for Process {
    fn drop(&mut self) {
        unsafe {
            let _ = CloseHandle(self.handle);
        }
    }
}