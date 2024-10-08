pub mod caste {
    use crate::win::memory::memory::{enum_mem_vec, read_mem};
    use crate::{types::{flagarray::FlagArray, memorylayout::MemorySection}, util::memory::read_mem_as_string, DFInstance};


    #[derive(Default, Debug, Clone)]
    pub struct Caste {
        pub address: usize,
        pub name: String,
        pub name_plural: String,
        pub description: String,
        pub flags: FlagArray,
        pub race: String,
        pub tag: String,
        pub baby_age: i32,
        pub child_age: i32,
        pub adult_size: i32,
        pub body_addr: usize,
        pub body_parts_addr: Vec<usize>,
    }

    impl Caste {
        pub unsafe fn new (df: &DFInstance, address: usize) -> Self {
            let mut c = Caste {
                address,
                ..Default::default()
            };

            c.tag = read_mem_as_string(&df.proc, address);
            c.name = read_mem_as_string(&df.proc, address + df.memory_layout.field_offset(MemorySection::Caste, "caste_name"));
            c.name_plural = read_mem_as_string(&df.proc, address + df.memory_layout.field_offset(MemorySection::Word, "noun_plural"));
            c.flags = FlagArray::new(&df, address + df.memory_layout.field_offset(MemorySection::Caste, "flags"));

            if c.flags.flags.get(97).unwrap_or_default() {
                c.baby_age = match read_mem::<i32>(&df.proc.handle, address + df.memory_layout.field_offset(MemorySection::Caste, "baby_age")) {
                    -1 => 0,
                    x => x
                };
            }

            if c.flags.flags.get(98).unwrap_or_default() {
                c.child_age = match read_mem::<i32>(&df.proc.handle, address + df.memory_layout.field_offset(MemorySection::Caste, "child_age")) {
                    -1 => 0,
                    x => x
                };
            }
            c.adult_size = read_mem::<i32>(&df.proc.handle, address + df.memory_layout.field_offset(MemorySection::Caste, "adult_size"));

            c.body_addr = address + df.memory_layout.field_offset(MemorySection::Caste, "body_info");
            c.body_parts_addr = enum_mem_vec(&df.proc.handle, c.body_addr);

            // convenience flag setting

            // butcherable
            if c.flags.flags.get(46).unwrap_or_default() {
                let _ = c.flags.flags.set(202, true);
            }

            let trainable: bool =
            c.flags.flags.get(53).unwrap_or_default() || // Hunting
            c.flags.flags.get(88).unwrap_or_default() || // War
            c.flags.flags.get(54).unwrap_or_default() || // Pet
            c.flags.flags.get(55).unwrap_or_default();   // Exotic Pet
            if trainable {
                let _ = c.flags.flags.set(203, true);
            }

            // fishable
            let not_fishable = c.flags.flags.get(37).unwrap_or_default();
            if not_fishable {
                let _ = c.flags.flags.set(26, false);
            }

            // extracts
            let extracts_vec_addr = address + df.memory_layout.field_offset(MemorySection::Caste, "extracts");
            let extracts = enum_mem_vec(&df.proc.handle, extracts_vec_addr);
            if extracts.len() > 0 {
                let _ = c.flags.flags.set(200, true);
            }

            // shared tissues
            let share_tissues_vec_addr = address + df.memory_layout.field_offset(MemorySection::Caste, "shearable_tissues_vector");
            let share_tissues = enum_mem_vec(&df.proc.handle, share_tissues_vec_addr);
            if share_tissues.len() > 0 {
                let _ = c.flags.flags.set(201, true);
            }

            c
        }

    }
}