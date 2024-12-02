pub mod caste {
    use serde::{Deserialize, Serialize};

    use crate::data::memorylayout::OffsetSection;
    use crate::win::memory::memory::{mem_vec, read_mem};
    use crate::win::process::Process;
    use crate::{flagarray::FlagArray, util::memory::read_mem_as_string, DFInstance};


    #[derive(Default, Debug, Clone, Serialize, Deserialize)]
    pub struct Caste {
        pub address: usize,
        pub tag: String,
        pub name: String,
        pub name_plural: String,
        pub description: String,
        pub baby_age: i32,
        pub child_age: i32,
        pub adult_size: i32,
        pub body_parts_addr: Vec<usize>,
        pub flags: FlagArray,
    }

    impl Caste {
        pub unsafe fn new (df: &DFInstance, proc: &Process, address: usize) -> Self {
            let mut c = Caste {
                address,
                tag:                read_mem_as_string(&proc, address),
                name:               read_mem_as_string(&proc, address + df.memory_layout.field_offset(OffsetSection::Caste, "caste_name")),
                name_plural:        read_mem_as_string(&proc, address + df.memory_layout.field_offset(OffsetSection::Word, "noun_plural")),
                adult_size:         read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Caste, "adult_size")),
                body_parts_addr:    mem_vec(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Caste, "body_info")),
                flags:              FlagArray::new(proc, address + df.memory_layout.field_offset(OffsetSection::Caste, "flags")),
                ..Default::default()
            };

            c.check_flags(proc, df);
            c
        }

        pub unsafe fn check_flags(&mut self, proc: &Process, df: &DFInstance) {
            if self.flags.flags.get(97).unwrap_or_default() {
                self.baby_age = match read_mem::<i32>(&proc.handle, self.address + df.memory_layout.field_offset(OffsetSection::Caste, "baby_age")) {
                    -1 => 0,
                    x => x
                };
            }

            if self.flags.flags.get(98).unwrap_or_default() {
                self.child_age = match read_mem::<i32>(&proc.handle, self.address + df.memory_layout.field_offset(OffsetSection::Caste, "child_age")) {
                    -1 => 0,
                    x => x
                };
            }

            // butcherable
            if self.flags.flags.get(46).unwrap_or_default() {
                let _ = self.flags.flags.set(202, true);
            }

            let trainable: bool = self.flags.flags.get(53).unwrap_or_default() || // Hunting
                self.flags.flags.get(88).unwrap_or_default() || // War
                self.flags.flags.get(54).unwrap_or_default() || // Pet
                self.flags.flags.get(55).unwrap_or_default();   // Exotic Pet

            if trainable {
                let _ = self.flags.flags.set(203, true);
            }

            // fishable
            let not_fishable = self.flags.flags.get(37).unwrap_or_default();
            if not_fishable {
                let _ = self.flags.flags.set(26, false);
            }

            // extracts
            let extracts = mem_vec::<usize>(&proc.handle, self.address + df.memory_layout.field_offset(OffsetSection::Caste, "extracts"));
            if extracts.len() > 0 {
                let _ = self.flags.flags.set(200, true);
            }

            // shared tissues
            let share_tissues = mem_vec::<usize>(&proc.handle, self.address + df.memory_layout.field_offset(OffsetSection::Caste, "shearable_tissues_vector"));
            if share_tissues.len() > 0 {
                let _ = self.flags.flags.set(201, true);
            }
        }
    }
}