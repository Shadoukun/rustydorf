pub mod race {
    use std::{fmt::Error, ops::Add};

    use crate::win::{memory::memory::enum_mem_vec, process::Process};

    use crate::util::address_plus_offset;
    use crate::{capitalize_each, DFInstance};
    use crate::util::memory::{read_field_as_string, read_field_as_vec, read_mem_as_string};
    use crate::types::memorylayout::{MemoryLayout, MemorySection};

    #[derive(Default, Debug)]
    pub struct Race {
        pub id: i32,
        pub name: String,
        pub plural_name: String,
        pub adjective: String,
        pub baby_name: String,
        pub baby_name_plural: String,
        pub child_name: String,
        pub child_name_plural: String,

        pub pref_strings: Vec<String>,
        pub pop_ratio_vector: usize,
        pub castes_vector: usize,
        pub castes: Vec<String>,

    }

    impl Race {
        pub fn new(df: &DFInstance, id: i32, base_addr: usize) -> Result<Self, Error> {
            let mut r: Race = Default::default();

            unsafe {
                r.id = id;
                r.name = read_field_as_string(&df.proc, base_addr, &df.memory_layout, MemorySection::Race, "name_singular")?;
                r.plural_name = read_field_as_string(&df.proc, base_addr, &df.memory_layout, MemorySection::Race, "name_plural")?;
                r.adjective = read_field_as_string(&df.proc, base_addr, &df.memory_layout, MemorySection::Race, "adjective")?;
                r.child_name = read_field_as_string(&df.proc, base_addr, &df.memory_layout, MemorySection::Race, "child_name_singular")?;
                r.child_name_plural = read_field_as_string(&df.proc, base_addr, &df.memory_layout, MemorySection::Race, "child_name_plural")?;
                r.baby_name = read_field_as_string(&df.proc, base_addr, &df.memory_layout, MemorySection::Race, "baby_name_singular")?;
                r.baby_name_plural = read_field_as_string(&df.proc, base_addr, &df.memory_layout, MemorySection::Race, "baby_name_plural")?;
            };

            if r.baby_name.is_empty() && !r.child_name.is_empty() {
                r.baby_name = r.child_name.clone();
                r.baby_name_plural = r.child_name_plural.clone();
            }
            if r.child_name.is_empty() && !r.baby_name.is_empty() {
                r.child_name = r.baby_name.clone();
                r.child_name_plural = r.baby_name_plural.clone();
            }

            if r.baby_name.is_empty() {
                r.baby_name = r.name.clone() + " Baby";
                r.baby_name_plural = r.plural_name.clone() + " Babies";
            }

            if r.child_name.is_empty() {
                r.child_name = r.name.clone() + " Offspring";
                r.child_name_plural = r.plural_name.clone() + " Offspring";
            }

            r.child_name = capitalize_each(&r.child_name);
            r.child_name_plural = capitalize_each(&r.child_name_plural);
            r.baby_name = capitalize_each(&r.baby_name);
            r.baby_name_plural = capitalize_each(&r.baby_name_plural);

            unsafe {
                let pref_string_vector_offset = df.memory_layout.field_offset(MemorySection::Race, "pref_string_vector");
                let pref_strings = enum_mem_vec(&df.proc.handle, base_addr.add(pref_string_vector_offset));
                for p in pref_strings {
                    let pref_string = read_mem_as_string(&df.proc, p);
                    r.pref_strings.push(pref_string);
                }
            }

            let pop_ratio_vector_offset = df.memory_layout.field_offset(MemorySection::Race, "pop_ratio_vector");
            let castes_vector_offset = df.memory_layout.field_offset(MemorySection::Race, "castes_vector");
            let materials_vector_offset = df.memory_layout.field_offset(MemorySection::Race, "materials_vector");
            let tissues_vector_offset = df.memory_layout.field_offset(MemorySection::Race, "tissues_vector");

            unsafe {
                let castes = enum_mem_vec(&df.proc.handle, base_addr.add(castes_vector_offset));
                if !castes.is_empty() {
                    for c in castes {
                        let caste_name = read_mem_as_string(&df.proc, c);
                        r.castes_vector = c;
                        r.castes.push(caste_name);
                        // todo: add caste details
                    }
                }
            }

            let dwarf_race_id = df.memory_layout.field_offset(MemorySection::Addresses, "dwarf_race_index");

            if r.id == dwarf_race_id as i32 {
                // todo: caste ratios
            }

            // todo: flag array

            Ok(r)
        }
    }
}