pub mod caste {
    use serde::{Deserialize, Serialize};

    use crate::data::memorylayout::OffsetSection;
    use crate::win::memory::memory::{enum_mem_vec, read_mem};
    use crate::win::process::Process;
    use crate::{types::flagarray::FlagArray, util::memory::read_mem_as_string, DFInstance};


    #[derive(Default, Debug, Clone, Serialize, Deserialize)]
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
        pub unsafe fn new (df: &DFInstance, proc: &Process, address: usize) -> Self {
            let mut c = Caste {
                address,
                ..Default::default()
            };

            c.tag = read_mem_as_string(&proc, address);
            c.name = read_mem_as_string(&proc, address + df.memory_layout.field_offset(OffsetSection::Caste, "caste_name"));
            c.name_plural = read_mem_as_string(&proc, address + df.memory_layout.field_offset(OffsetSection::Word, "noun_plural"));
            c.flags = FlagArray::new(&df, proc, address + df.memory_layout.field_offset(OffsetSection::Caste, "flags"));

            if c.flags.flags.get(97).unwrap_or_default() {
                c.baby_age = match read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Caste, "baby_age")) {
                    -1 => 0,
                    x => x
                };
            }

            if c.flags.flags.get(98).unwrap_or_default() {
                c.child_age = match read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Caste, "child_age")) {
                    -1 => 0,
                    x => x
                };
            }
            c.adult_size = read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Caste, "adult_size"));

            c.body_addr = address + df.memory_layout.field_offset(OffsetSection::Caste, "body_info");
            c.body_parts_addr = enum_mem_vec(&proc.handle, c.body_addr);

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
            let extracts_vec_addr = address + df.memory_layout.field_offset(OffsetSection::Caste, "extracts");
            let extracts = enum_mem_vec(&proc.handle, extracts_vec_addr);
            if extracts.len() > 0 {
                let _ = c.flags.flags.set(200, true);
            }

            // shared tissues
            let share_tissues_vec_addr = address + df.memory_layout.field_offset(OffsetSection::Caste, "shearable_tissues_vector");
            let share_tissues = enum_mem_vec(&proc.handle, share_tissues_vec_addr);
            if share_tissues.len() > 0 {
                let _ = c.flags.flags.set(201, true);
            }

            c
        }

    }
}