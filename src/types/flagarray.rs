use crate::win::memory::memory::read_mem;
use crate::DFInstance;

pub struct FlagArray {
    pub address: usize,
    pub flags: BitArray,
}

impl FlagArray {
        pub unsafe fn new(df: &DFInstance, address: usize) -> Self {
            let mut flags_addr = read_mem::<usize>(&df.proc.handle, address);
            let size_in_bytes = read_mem::<u32>(&df.proc.handle, address + 4) as usize;

            if size_in_bytes > 1000 {
                println!("FlagArray size is too large: {}", size_in_bytes);
                return FlagArray {
                    address,
                    flags: BitArray::new(0),
                };
            }

            let mut flags = BitArray::new(size_in_bytes * 8);
            for i in 0..size_in_bytes {
                let mut pos = 7;
                let byte = read_mem::<u8>(&df.proc.handle, flags_addr);
                if byte > 0 {
                    let mut iter = 128;
                    while iter > 0 {
                        let _ = flags.set(i * 8 + pos, true);
                        pos -= 1;
                        iter /= 2;
                    }
                }
                flags_addr += 1;
            }
            FlagArray {
            address,
            flags,
        }
    }
}

impl Default for FlagArray {
    fn default() -> Self {
        FlagArray{
            address: 0,
            flags: BitArray::new(0)
        }
    }
}

pub struct BitArray {
    data: Vec<u8>, // Each byte holds 8 bits
    size: usize,   // Track the number of bits
}

impl BitArray {
    pub fn new(size: usize) -> Self {
        let byte_size = (size + 7) / 8;
        BitArray {
            data: vec![0; byte_size],
            size,
        }
    }

     pub fn get(&self, index: usize) -> Option<bool> {
        if index >= self.size {
            return None;
        }
        let byte = self.data[index / 8];
        let bit = 1 << (index % 8);
        Some(byte & bit != 0)
    }

    pub fn set(&mut self, index: usize, value: bool) -> Result<(), &'static str> {
        if index >= self.size {
            return Err("Index out of bounds");
        }
        let byte = &mut self.data[index / 8];
        let bit = 1 << (index % 8);
        if value {
            *byte |= bit; // Set the bit to 1
        } else {
            *byte &= !bit; // Clear the bit
        }
        Ok(())
    }

    pub fn size(&self) -> usize {
        self.size
    }
}