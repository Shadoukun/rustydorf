
use crate::win::process::Process;
use crate::DEFAULT_BASE_ADDR;

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
pub unsafe fn address_plus_offset(proc: &Process, mut offset: usize) -> usize {
    offset = offset.wrapping_sub(DEFAULT_BASE_ADDR as usize);
    proc.modules[0].modBaseAddr.add(offset) as usize
}

pub mod memory {
    use std::fmt::Error;

    use crate::win::{memory::memory::{enum_mem_vec, read_mem, read_raw}, process::Process};
    use crate::types::memorylayout::{MemoryLayout, MemorySection};

    const STRING_BUFFER_LENGTH: usize = 16;
    const POINTER_SIZE: usize = std::mem::size_of::<usize>();

    /// Read memory from a process plus the given offset, and return it as a string
    pub unsafe fn read_mem_as_string(proc: &Process, offset: usize) -> String {
        let len = read_mem::<i32>(&proc.handle, offset + STRING_BUFFER_LENGTH);
        let _cap = read_mem::<i32>(&proc.handle, offset + STRING_BUFFER_LENGTH + POINTER_SIZE);
        let mut buf = vec![0; len as usize];
        read_raw(&proc.handle, offset, len as usize, buf.as_mut_ptr());
        String::from_utf8_lossy(&buf).to_string()
    }

    /*
    Field reading functions
    */

    /// Read a given MemoryLayout field from the given address, and return it as Result<T, Error>
    pub unsafe fn read_field<T: Default>(
        proc: &Process,
        offset: usize,
        layout: &MemoryLayout,
        section: MemorySection,
        field: &str,
    ) -> Result<T, Error> {
        let field_offset = layout.field_offset(section, field);
        Ok(read_mem::<T>(&proc.handle, offset + field_offset))
    }

    /// Read a given MemoryLayout field from the given address, and return a Result<String, Error>
    pub unsafe fn read_field_as_string(
        proc: &Process,
        offset: usize,
        layout: &MemoryLayout,
        section: MemorySection,
        field: &str,
    ) -> Result<String, Error> {
        let field_offset = layout.field_offset(section, field);
        Ok(read_mem_as_string(proc, offset + field_offset))
    }

    /// Read a given MemoryLayout field from the given address, and return a Result<Vec<usize>, Error>
    pub unsafe fn read_field_as_vec(
        proc: &Process,
        offset: usize,
        layout: &MemoryLayout,
        section: MemorySection,
        field: &str
    ) -> Result<Vec<usize>, Error> {
        let field_offset = layout.field_offset(section, field);
        let result = enum_mem_vec(&proc.handle, offset + field_offset);
        Ok(result)
    }

}
