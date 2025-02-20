
use crate::win::{memory::memory::DEFAULT_BASE_ADDR, process::Process};

/// Capitalize the first letter of each word in a string
pub fn capitalize_each(input: &str) -> String {
    input.split_whitespace()
         .map(|word| {
             let mut chars = word.chars();
             match chars.next() {
                 Some(first_char) => first_char.to_uppercase().collect::<String>() + chars.as_str(),
                 None => String::new(),
             }
         })
         .collect::<Vec<String>>()
         .join(" ")
}

/// returns the address of the given process module plus the given offset
/// Used for global addresses
pub unsafe fn global_address(proc: &Process, mut offset: usize) -> usize {
    offset = offset.wrapping_sub(DEFAULT_BASE_ADDR as usize);
    proc.modules[0].modBaseAddr.add(offset) as usize
}

pub mod memory {
    use codepage_437::{FromCp437,CP437_CONTROL} ;

    use crate::win::{memory::memory::{read_mem, read_raw}, process::Process};

    const STRING_BUFFER_LENGTH: usize = 16;
    const POINTER_SIZE: usize = std::mem::size_of::<usize>();

    // writing this as a common trait implementation with read_mem would be better,
    // but due to how Rust infers generics, if it was a trait I wouldn't be able
    // to use the `read_mem::<T>` syntax directly and I'd have to use to use `T as ReadMem::read_mem` instead.
    // hopefully this will be fixed in the future. Nightlies?

    /// Read memory from a process plus the given offset, and return it as a string
    pub unsafe fn read_mem_as_string(proc: &Process, mut offset: usize) -> String {
        let len = read_mem::<i32>(&proc.handle, offset + STRING_BUFFER_LENGTH) as usize;
        let cap = read_mem::<i32>(&proc.handle, offset + STRING_BUFFER_LENGTH + POINTER_SIZE) as usize;
        if cap > STRING_BUFFER_LENGTH {
            offset = read_mem::<usize>(&proc.handle, offset);
        }
        if len > 1024 {
            return String::new();
        }
        let mut buf = vec![0; len as usize];
        read_raw(&proc.handle, offset, len, buf.as_mut_ptr());
        // Dwarf Fortress uses CP437 encoding for strings
        String::from_cp437(buf, &CP437_CONTROL)
    }
}
