pub mod memory {
    use std::ffi::c_void;
    use std::ptr::null_mut;

    use windows::Win32::Foundation::{GetLastError, WIN32_ERROR};
    use windows::Win32::System::Diagnostics::Debug::{ReadProcessMemory, WriteProcessMemory};
    use windows::Win32::Foundation::HANDLE;

    #[cfg(target_arch = "x86")]
    pub const DEFAULT_BASE_ADDR:  u32 = 0x400000;
    #[cfg(target_arch = "x86_64")]
    pub const DEFAULT_BASE_ADDR: u64 = 0x140000000;


    pub unsafe fn read_raw(
        process_handle: &HANDLE,
        base_address: usize,
        size: usize,
        buffer: *mut u8,
    ) -> usize {
        let mut bytes_read: usize = 0;
        let _ = ReadProcessMemory(
            *process_handle,
            base_address as *mut _,
            buffer as *mut _,
            size,
            Some(&mut bytes_read),
        );
        bytes_read
    }

    pub unsafe fn write_raw(
        process_handle: &HANDLE,
        base_address: usize,
        size: usize,
        buffer: *mut u8,
    ) -> usize {
        let mut bytes_written: usize = 0;
        let _ = WriteProcessMemory(
            *process_handle,
            base_address as *mut _,
            buffer as *mut _,
            size,
            Some(&mut bytes_written),
        );
        bytes_written
    }

    /// A generic function to wrap ReadProcessMemory and return as a generic type T
    pub unsafe fn read_mem<T: Default>(
        process_handle: &HANDLE,
        base_address: usize,
    ) -> T {
            let mut res: T = Default::default();

            let _ = match ReadProcessMemory(
                *process_handle,
                base_address as *mut c_void,
                &mut res as *mut T as *mut c_void,
                std::mem::size_of::<T>(),
                Some(null_mut::<usize>()),
            ) {
                Ok(x) => x,
                Err(_) => {
                    let error_code: WIN32_ERROR = GetLastError();
                    println!("Read Failed: {:?}", error_code);
                }
        };
        res
    }

    /// A generic function to wrap WriteProcessMemory
    pub unsafe fn write_mem<T>(
        process_handle: &HANDLE,
        base_address: usize,
        value: T,
    ) {
        let _ = match WriteProcessMemory(
            *process_handle,
            base_address as *mut c_void,
            &value as *const T as *const c_void,
            std::mem::size_of::<T>(),
            Some(null_mut::<usize>()),
        ) {
            Ok(x) => x,
            Err(_) => {
                let error_code: WIN32_ERROR = GetLastError();
                println!("Write Failed. Code: {:?}", error_code);
            }
        };
    }

    pub unsafe fn enum_mem_vec<T: Default + Clone>(proc: &HANDLE, addr: usize) -> Vec<T> {
        let pointer_size = std::mem::size_of::<T>();
        let start = read_mem::<usize>(proc, addr);
        let end = read_mem::<usize>(proc, addr + pointer_size);
        let count = (end - start) / pointer_size;

        let mut out = vec![T::default(); count];
        read_raw(proc, start, (end - start) as usize, out.as_mut_ptr() as *mut u8);

        out
    }

    // /// A function to enumerate a vector of memory addresses from a given address
    // pub unsafe fn enum_mem_vec(proc: &HANDLE, addr: usize) -> Vec<usize> {
    //     let pointer_size = std::mem::size_of::<usize>();
    //     let start = read_mem::<usize>(proc, addr);
    //     let end = read_mem::<usize>(proc, addr + pointer_size);
    //     let count = (end - start) / pointer_size;

    //     let mut out = vec![0; count];
    //     read_raw(proc, start, (end - start) as usize, out.as_mut_ptr() as *mut u8);

    //     out
    // }

}